def calculate_category_score(constants, tallies):
    score = sum(constants[key] * tallies[key] for key in constants)

    return score


def calculate_total_engagement_score(sec, eec, cec, iec):
    tes = sec + eec + cec + iec

    return tes


def calculate_percentage(score, tes):
    percentage = (score / tes) * 100 if tes != 0 else 0

    return percentage


def calculate_engagement_scores(tallies):
    # Define the constants for each engagement category
    socialization_constants = {
        "post_blog": 0.5,
        "send_chat_message": 0.01,
        "post_forum": 0.25,
        "image_sharing": 0.002,
        "video_sharing": 0.002,
        "text_resource_sharing": 0.002,
        "created_topic": 0.025,
    }

    externalization_constants = {
        "post_blog": 0.5,
        "send_chat_message": 0.001,
        "post_forum": 0.25,
        "created_topic": 0.025,
        "comment": 0.002,
    }

    combination_constants = {
        "created_topic": 0.025,
        "post_blog": 0.5,
    }

    internalization_constants = {
        "used_in_app_browser": 0.001,
        "read_blog": 0.001,
        "read_forum": 0.001,
        "recieve_chat_message": 0.001,
        "download_resources": 0.001,
    }

    # Print values for debugging
    # print("Tallies:", tallies)

    # Calculate Socialization Engagement Score (SEC)
    sec = calculate_category_score(socialization_constants, tallies)

    # Calculate Externalization Engagement Score (EEC)
    eec = calculate_category_score(externalization_constants, tallies)

    # Calculate Combination Engagement Score (CEC)
    cec = calculate_category_score(combination_constants, tallies)

    # Calculate Internalization Engagement Score (IEC)
    iec = calculate_category_score(internalization_constants, tallies)

    # Calculate Total Engagement Score (TES)
    tes = calculate_total_engagement_score(sec, eec, cec, iec)

    # Calculate engagement percentages for each category
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
