import requests
import json
from typing import Dict, List, Optional, Union

def get_voting_data() -> Dict[str, Union[bool, str, List[Dict]]]:
    """
    Retrieves a list of all available Swiss federal voting proposals and their metadata from opendata.swiss.
    
    This function accesses the Swiss open data portal to fetch information about federal voting proposals.
    It returns metadata about each vote, including dates, descriptions, and URLs to detailed results.
    No authentication is required to access this API.

    Returns:
        Dict[str, Union[bool, str, List[Dict]]]: A dictionary with the following structure:
            {
                'success': bool,  # Whether the API request was successful
                'error': str | None,  # Error message if any occurred
                'data': List[Dict]  # List of voting resources, where each dict contains:
                    {
                        'date': str,  # Coverage date in format 'YYYY-MM-DD'
                        'description': str,  # English description of the vote
                        'download_url': str,  # URL to download detailed results
                        'format': str,  # Data format (usually 'JSON')
                        'last_modified': str  # Last modification timestamp
                    }
            }

    Example:
        >>> result = get_voting_data()
        >>> if result['success']:
        >>>     # Print all available votes
        >>>     for vote in result['data']:
        >>>         print(f"Vote on {vote['date']}: {vote['description']}")
        >>> else:
        >>>     print(f"Error: {result['error']}")
    """
    # API endpoint URL
    url = "https://ckan.opendata.swiss/api/3/action/package_show"
    
    # Query parameters
    params = {
        "id": "echtzeitdaten-zu-den-eidgenossischen-abstimmungen-gemeindestand-am-datum-der-abstimmung"
    }
    
    result = {
        'success': False,
        'error': None,
        'data': []
    }
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        if data["success"]:
            result['success'] = True
            resources = data["result"]["resources"]
            
            for resource in resources:
                resource_data = {
                    'date': resource.get("coverage", "No date available"),
                    'description': resource.get("description", {}).get("en", "No description available"),
                    'download_url': resource.get("download_url", "No URL available"),
                    'format': resource.get("format", "Unknown format"),
                    'last_modified': resource.get("last_modified", "Unknown")
                }
                result['data'].append(resource_data)
                
        else:
            result['error'] = "API request was not successful"
            
    except requests.exceptions.RequestException as e:
        result['error'] = f"Error making API request: {str(e)}"
    except json.JSONDecodeError as e:
        result['error'] = f"Error parsing JSON response: {str(e)}"
    except Exception as e:
        result['error'] = f"An unexpected error occurred: {str(e)}"
    
    return result

def get_voting_summary(proposal_name: str) -> Dict[str, Union[bool, str, Dict]]:
    """
    Retrieves and summarizes detailed results for a specific Swiss federal voting proposal.
    
    This function first searches for a proposal matching the given name, then fetches and
    summarizes its voting results. The proposal name can be partial but should be specific
    enough to match the correct vote.

    Args:
        proposal_name (str): The name or description of the voting proposal to search for.
            Can be provided in two formats:
            1. Full format: "Federal proposals: 1. Popular Initiative 'Initiative Name'"
            2. Simple format: "Initiative Name"
            The text between single quotes (if present) is used for matching.

    Returns:
        Dict[str, Union[bool, str, Dict]]: A dictionary with the following structure:
            {
                'success': bool,  # Whether the data was successfully retrieved
                'error': str | None,  # Error message if any occurred
                'summary': {  # Only present if success is True
                    'title': str,  # English title (falls back to German if English unavailable)
                    'date': str,  # Vote date in format 'YYYYMMDD'
                    'accepted': bool,  # Whether the proposal was accepted
                    'turnout': float,  # Voter turnout percentage
                    'yes_percentage': float,  # Percentage of yes votes
                    'yes_votes': int,  # Number of yes votes
                    'no_votes': int,  # Number of no votes
                    'eligible_voters': int,  # Number of eligible voters
                    'all_titles': Dict[str, str]  # Titles in all available languages
                }
            }

    Examples:
        >>> # Using full format
        >>> result = get_voting_summary("Federal proposals: 1. Popular Initiative 'For a responsible economy'")
        >>> 
        >>> # Using simple format
        >>> result = get_voting_summary("For a responsible economy")
        >>> 
        >>> if result['success']:
        >>>     summary = result['summary']
        >>>     print(f"The proposal was {'accepted' if summary['accepted'] else 'rejected'}")
        >>>     print(f"Turnout: {summary['turnout']}%")
        >>>     print(f"Yes votes: {summary['yes_votes']:,} ({summary['yes_percentage']:.1f}%)")
        >>> else:
        >>>     print(f"Error: {result['error']}")
    """
    result = {
        'success': False,
        'error': None,
        'summary': None
    }
    
    try:
        # First get the list of votes
        url = "https://ckan.opendata.swiss/api/3/action/package_show"
        params = {
            "id": "echtzeitdaten-zu-den-eidgenossischen-abstimmungen-gemeindestand-am-datum-der-abstimmung"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data["success"]:
            result['error'] = "Failed to retrieve voting data list"
            return result
            
        # Find the matching vote and its URL
        matching_resource = None
        # Clean up the search term - extract the main part of the initiative name
        if "'" in proposal_name:
            # Extract text between single quotes
            search_term = proposal_name.split("'")[1].lower().strip()
        else:
            search_term = proposal_name.lower().replace("federal proposals:", "").strip()
        
        print(f"Searching for proposal containing: '{search_term}'")
        
        for resource in data["result"]["resources"]:
            description = resource.get("description", {}).get("en", "").lower()
            
            # Print for debugging
            print(f"\nChecking resource: {description}")
            
            # More precise matching - require a significant overlap
            if search_term in description:
                matching_resource = resource
                print(f"Found match: {description}")
                break
        
        if not matching_resource:
            result['error'] = f"No voting data found for proposal: {proposal_name}"
            return result
            
        # Get the detailed results
        results_url = matching_resource['download_url']
        print(f"Found matching proposal. Fetching results from: {results_url}")
        
        results_response = requests.get(results_url)
        results_response.raise_for_status()
        voting_results = results_response.json()
        
        # Extract the summary from the new JSON structure
        if 'schweiz' in voting_results and 'vorlagen' in voting_results['schweiz']:
            vote_info = voting_results['schweiz']['vorlagen'][0]  # Get first vote
            national_result = vote_info['resultat']
            
            # Get titles in all available languages
            titles = {title['langKey']: title['text'] for title in vote_info['vorlagenTitel']}
            
            result['success'] = True
            result['summary'] = {
                'title': titles.get('en', titles.get('de', 'Title not available')),  # Prefer English, fallback to German
                'date': voting_results['abstimmtag'],  # Format: YYYYMMDD
                'accepted': vote_info['vorlageAngenommen'],
                'turnout': national_result['stimmbeteiligungInProzent'],
                'yes_percentage': national_result['jaStimmenInProzent'],
                'yes_votes': national_result['jaStimmenAbsolut'],
                'no_votes': national_result['neinStimmenAbsolut'],
                'eligible_voters': national_result['anzahlStimmberechtigte'],
                'all_titles': titles  # Include all language versions
            }
        else:
            result['error'] = "Could not find voting results in the data"
            
    except requests.exceptions.RequestException as e:
        result['error'] = f"Error making API request: {str(e)}"
    except json.JSONDecodeError as e:
        result['error'] = f"Error parsing JSON response: {str(e)}"
    except Exception as e:
        result['error'] = f"An unexpected error occurred: {str(e)}"
    
    return result

if __name__ == "__main__":
    # Example usage with formatted output
    result = get_voting_data()
    if result['success']:
        print("Available voting data:")
        print("-" * 50)
        for resource in result['data']:
            print(f"Date: {resource['date']}")
            print(f"Description: {resource['description']}")
            print(f"Download URL: {resource['download_url']}")
            print(f"Format: {resource['format']}")
            print(f"Last Modified: {resource['last_modified']}")
            print("-" * 50)
    else:
        print(f"Error: {result['error']}")

    # Example usage
    proposal = "Federal proposals: 1. Popular Initiative 'For a responsible economy within our planet's limits'"
    result = get_voting_summary(proposal)
    
    if result['success']:
        summary = result['summary']
        print("\nVoting Summary:")
        print("-" * 50)
        print(f"Title (English): {summary['title']}")
        print(f"Date: {summary['date'][:4]}-{summary['date'][4:6]}-{summary['date'][6:]}")  # Format YYYY-MM-DD
        print(f"Result: {'Accepted' if summary['accepted'] else 'Rejected'}")
        print(f"Turnout: {summary['turnout']:.1f}%")
        print(f"Yes Percentage: {summary['yes_percentage']:.1f}%")
        print(f"Yes Votes: {summary['yes_votes']:,}")
        print(f"No Votes: {summary['no_votes']:,}")
        print(f"Eligible Voters: {summary['eligible_voters']:,}")
        
        # Print titles in all languages
        print("\nTitles in all languages:")
        for lang, title in summary['all_titles'].items():
            print(f"{lang.upper()}: {title}")
    else:
        print(f"Error: {result['error']}")
