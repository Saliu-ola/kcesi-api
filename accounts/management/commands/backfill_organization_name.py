"""
Management command: backfill_organization_name

Fixes existing users who registered via the external invitation link and ended up
with organization_id set but organization_name = null.  This caused group-membership
and group-leader assignment to fail for those users.

Usage:
    python manage.py backfill_organization_name            # dry-run (safe, no writes)
    python manage.py backfill_organization_name --apply    # actually update the DB
"""

from django.core.management.base import BaseCommand
from accounts.models import User
from organization.models import Organization


class Command(BaseCommand):
    help = (
        "Backfill organization_name for users that have organization_id "
        "but a null organization_name (typically external-link registrants)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Actually write changes to the database. Without this flag the command runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        apply = options["apply"]

        if not apply:
            self.stdout.write(
                self.style.WARNING(
                    "DRY-RUN mode — no changes will be saved. "
                    "Pass --apply to persist the fixes.\n"
                )
            )

        # Only target users who have an org ID but are missing the org name
        affected_users = User.objects.filter(
            organization_id__isnull=False,
            organization_name__isnull=True,
        ).exclude(organization_id="")

        total = affected_users.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No affected users found. Nothing to do."))
            return

        self.stdout.write(f"Found {total} user(s) with missing organization_name.\n")

        fixed = 0
        skipped = 0

        for user in affected_users:
            try:
                org = Organization.objects.get(organization_id=user.organization_id)
            except Organization.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"  SKIP  user id={user.id} email={user.email} — "
                        f"organization_id '{user.organization_id}' not found in Organization table."
                    )
                )
                skipped += 1
                continue

            self.stdout.write(
                f"  {'UPDATE' if apply else 'WOULD UPDATE'}  "
                f"user id={user.id} email={user.email}  ->  organization_name='{org.name}'"
            )

            if apply:
                user.organization_name = org.name
                user.save(update_fields=["organization_name"])
                fixed += 1
            else:
                fixed += 1  # count as "would fix" in dry-run

        self.stdout.write("")
        if apply:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Fixed: {fixed}  |  Skipped (no org record): {skipped}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry-run complete. Would fix: {fixed}  |  Would skip: {skipped}\n"
                    "Run with --apply to save changes."
                )
            )
