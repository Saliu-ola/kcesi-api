from decimal import Decimal, ROUND_DOWN, DivisionUndefined
import decimal


def calculate_ai_division(ai_score, count):
    try:
        ai_score = Decimal(ai_score)
        count = Decimal(count)
        if count == 0:
            return Decimal("0.00")
        result = ai_score / count
    except (ZeroDivisionError, DivisionUndefined, decimal.InvalidOperation):
        result = Decimal("0.00")
    return result


# def calculate_category_score(constants, tallies):
#     score = sum(Decimal(constants[key]) * Decimal(tallies[key]) for key in constants)
#     return score


def calculate_category_score(constants, tallies):
    score = sum(
        Decimal(constants[key]) * Decimal(tallies.get(key, 0)) for key in constants
    )
    return score


def calculate_total_engagement_score(sec, eec, cec, iec):
    sec = Decimal(sec)
    eec = Decimal(eec)
    cec = Decimal(cec)
    iec = Decimal(iec)
    tes = sec + eec + cec + iec
    return tes


# def calculate_total_engagement_score(sec, eec, cec, iec):
#     tes = sec + eec + cec + iec

#     return tes


def calculate_percentage(score, tes):
    percentage = (Decimal(score) / Decimal(tes)) * 100 if tes != 0 else 0
    return percentage


def calculate_engagement_scores(tallies):
    socialization_constants = {
        "post_blog": Decimal("0.5"),
        "send_chat_message": Decimal("0.01"),
        "post_forum": Decimal("0.25"),
        "image_sharing": Decimal("0.002"),
        "video_sharing": Decimal("0.002"),
        "text_resource_sharing": Decimal("0.002"),
        "created_topic": Decimal("0.025"),
    }

    externalization_constants = {
        "post_blog": Decimal("0.5"),
        "send_chat_message": Decimal("0.001"),
        "post_forum": Decimal("0.25"),
        "created_topic": Decimal("0.025"),
        "comment": Decimal("0.002"),
    }

    combination_constants = {
        "created_topic": Decimal("0.025"),
        "post_blog": Decimal("0.5"),
    }

    internalization_constants = {
        "used_in_app_browser": Decimal("0.001"),
        "read_blog": Decimal("0.001"),
        "read_forum": Decimal("0.001"),
        "recieve_chat_message": Decimal("0.001"),
        "download_resources": Decimal("0.001"),
    }

    sec = calculate_category_score(socialization_constants, tallies)
    eec = calculate_category_score(externalization_constants, tallies)
    cec = calculate_category_score(combination_constants, tallies)
    iec = calculate_category_score(internalization_constants, tallies)

    tes = calculate_total_engagement_score(sec, eec, cec, iec)

    socialization_percentage = calculate_percentage(sec, tes)
    externalization_percentage = calculate_percentage(eec, tes)
    combination_percentage = calculate_percentage(cec, tes)
    internalization_percentage = calculate_percentage(iec, tes)

    return {
        "socialization_engagement_score": sec,
        "externalization_engagement_score": eec,
        "combination_engagement_score": cec,
        "internalization_engagement_score": iec,
        "total_engagement_score": tes,
        "socialization_engagement_percentage": socialization_percentage,
        "externalization_engagement_percentage": externalization_percentage,
        "combination_engagement_percentage": combination_percentage,
        "internalization_engagement_percentage": internalization_percentage,
    }


def calculate_categorized_percentage(leaders):
    total = sum([score['percentage'] for score in leaders])
    if total == 0:
        return [{"user": data['user'], "percentage": "0.00"} for data in leaders]
    else:
        individual_categorized_percentage_list = [
            {
                "user": data['user'],
                "percentage": "{:.2f}".format(
                    (Decimal(data['percentage']) * Decimal('100.00')) / total
                ),
            }
            for data in leaders
        ]

        leaders_sorted = sorted(
            individual_categorized_percentage_list,
            key=lambda x: float(x['percentage']),
            reverse=True,
        )
        return leaders_sorted


# # Example usage
# tallies_example = {
#     "post_blog": 1,
#     "send_chat_message": 2,
#     "post_forum": 3,
#     "image_sharing": 4,
#     "video_sharing": 7,
#     "text_resource_sharing": 4,
#     "created_topic": 5,
#     "comment": 4,
#     "used_in_app_browser": 1,
#     "read_blog": 1,
#     "read_forum": 2,
#     "recieve_chat_message": 3,
#     "download_resources": 4,
# }

# result = calculate_engagement_scores(tallies_example)
# print(result)
