import urllib.parse

def build_dice_url(keyword, posted_date, easy_apply, employment_type, work_setting, location):
    """
    Constructs the Dice.com search URL based on user inputs.
    """
    base_url = "https://www.dice.com/jobs"
    
    # Base parameters
    params = {
        "q": keyword,
        "countryCode": "US",
        "locationPrecision": "State", # Defaulting to State for broad match, can be adjusted
        "location": location
    }

    # -- Posted Date Logic --
    # "Today" -> ONE
    # "Last 3 days" -> THREE
    # "Last 7 days" -> SEVEN
    if "Today" in posted_date:
        params["filters.postedDate"] = "ONE"
    elif "3" in posted_date:
        params["filters.postedDate"] = "THREE"
    elif "7" in posted_date:
        params["filters.postedDate"] = "SEVEN"
    
    # -- Easy Apply Logic --
    if easy_apply:
        params["filters.easyApply"] = "true"

    # -- Employment Type Logic --
    # Input expected as a list or comma-separated string, e.g. ["Full time", "Contract"]
    emp_types_map = {
        "Full time": "FULLTIME",
        "Contract": "CONTRACTS",
        "Part time": "PARTTIME",
        "Third Party": "THIRD_PARTY"
    }
    
    selected_emp_types = []
    # If input is string "Full time, Contract", split it. If list, iterate.
    if isinstance(employment_type, str):
        # normalize
        types_list = [t.strip() for t in employment_type.split(',')]
    else:
        types_list = employment_type

    for t in types_list:
        # Simple fuzzy matching or direct key lookup
        for key, val in emp_types_map.items():
            if key.lower() in t.lower():
                selected_emp_types.append(val)
    
    if selected_emp_types:
        params["filters.employmentType"] = "|".join(selected_emp_types)

    # -- Work Setting Logic --
    # Remote, Hybrid, Onsite
    setting_map = {
        "Remote": "REMOTE",
        "Hybrid": "HYBRID",
        "Onsite": "ONSITE"
    }
    
    selected_settings = []
    if isinstance(work_setting, str):
        settings_list = [s.strip() for s in work_setting.split(',')]
    else:
        settings_list = work_setting

    for s in settings_list:
        for key, val in setting_map.items():
            if key.lower() in s.lower():
                selected_settings.append(val)

    if selected_settings:
        params["filters.workSetting"] = "|".join(selected_settings)

    # Construct final URL
    query_string = urllib.parse.urlencode(params, safe='|')
    final_url = f"{base_url}?{query_string}"
    
    return final_url


def build_monster_url(keyword, posted_date, easy_apply, employment_type, work_setting, location):
    """
    Constructs the Monster.com search URL based on user inputs.
    """
    base_url = "https://www.monster.com/jobs/search"
    
    # Base parameters
    params = {
        "q": keyword,
    }
    
    # Location handling
    if location and location.lower() != "remote":
        params["where"] = location
    else:
        params["where"] = "Remote"
    
    # -- Posted Date Logic --
    # Monster uses different date filters
    # "Today" -> 1
    # "Last 3 days" -> 3
    # "Last 7 days" -> 7
    if "Today" in posted_date:
        params["tm"] = "1"  # Today
    elif "3" in posted_date:
        params["tm"] = "3"  # Last 3 days
    elif "7" in posted_date:
        params["tm"] = "7"  # Last 7 days
    
    # -- Easy Apply Logic --
    # Monster uses "easyapply" parameter
    if easy_apply:
        params["easyapply"] = "true"
    
    # -- Employment Type Logic --
    # Monster uses different employment type codes
    emp_types_map = {
        "Full time": "Full+Time",
        "Contract": "Contract",
        "Part time": "Part+Time",
        "Third Party": "Contract+To+Perm"
    }
    
    selected_emp_types = []
    if isinstance(employment_type, str):
        types_list = [t.strip() for t in employment_type.split(',')]
    else:
        types_list = employment_type

    for t in types_list:
        for key, val in emp_types_map.items():
            if key.lower() in t.lower():
                selected_emp_types.append(val)
    
    if selected_emp_types:
        params["et"] = ",".join(selected_emp_types)

    # -- Work Setting Logic --
    # Monster uses "worktype" parameter
    setting_map = {
        "Remote": "Remote",
        "Hybrid": "Hybrid",
        "Onsite": "On-Site"
    }
    
    selected_settings = []
    if isinstance(work_setting, str):
        settings_list = [s.strip() for s in work_setting.split(',')]
    else:
        settings_list = work_setting

    for s in settings_list:
        for key, val in setting_map.items():
            if key.lower() in s.lower():
                selected_settings.append(val)

    if selected_settings:
        params["worktype"] = ",".join(selected_settings)

    # Construct final URL
    query_string = urllib.parse.urlencode(params)
    final_url = f"{base_url}?{query_string}"
    
    return final_url


def build_job_url(job_board, keyword, posted_date, easy_apply, employment_type, work_setting, location):
    """
    Universal URL builder that routes to the appropriate job board.
    
    Args:
        job_board: 'dice' or 'monster'
        keyword: Job search keyword
        posted_date: Posted date filter
        easy_apply: Easy apply filter
        employment_type: Employment type filter
        work_setting: Work setting filter
        location: Location filter
    
    Returns:
        Search URL for the specified job board
    """
    if job_board.lower() == "monster":
        return build_monster_url(keyword, posted_date, easy_apply, employment_type, work_setting, location)
    else:
        return build_dice_url(keyword, posted_date, easy_apply, employment_type, work_setting, location)


# Example usage for testing
if __name__ == "__main__":
    test_url = build_dice_url(
        keyword="Java",
        posted_date="Last 3 days",
        easy_apply=True,
        employment_type="Contract, Third Party",
        work_setting="Remote",
        location="United States"
    )
    print("Generated Dice URL:", test_url)
    
    # Test Monster URL
    monster_url = build_monster_url(
        keyword="Python Developer",
        posted_date="Last 7 days",
        easy_apply=True,
        employment_type="Full time",
        work_setting="Remote",
        location="United States"
    )
    print("Generated Monster URL:", monster_url)
    
    # Test universal builder
    universal_url = build_job_url(
        job_board="monster",
        keyword="Data Scientist",
        posted_date="Today",
        easy_apply=True,
        employment_type="Full time",
        work_setting="Remote",
        location="New York"
    )
    print("Generated Universal URL:", universal_url)
