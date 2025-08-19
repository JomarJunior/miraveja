import requests
import json
import datetime

errors_dict = {
    # 1xx Informational
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    
    # 2xx Success
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    
    # 3xx Redirection
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    
    # 4xx Client Errors
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a Teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    
    # 5xx Server Errors
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
    520: "Web Server Returned an Unknown Error",
    521: "Web Server Is Down",
    522: "Connection Timed Out",
    523: "Origin Is Unreachable",
    524: "Timeout Occurred",
    525: "SSL Handshake Failed",
    526: "Invalid SSL Certificate"
}

base_url = "https://civitai.com/api/v1/"

params = {
    "limit": 200,
    "modelVersionId": 1612720,
    "nsfw": "X",
    "sort": "Most Reactions",
    "period": "AllTime",
    "cursor": "0",
}

headers = {
    "Authorization": "Bearer adc9b46ac9c4e4c63a36c5fbbd6e1b60",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache"
}

def calculate_time(function):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = function(*args, **kwargs)
        end_time = datetime.datetime.now()
        print(f"Time taken by {function.__name__}: {end_time - start_time}")
        return result
    return wrapper

def calculate_reactions(image) -> int:
    stats = image.get("stats")
    return stats.get("cryCount", 0) + stats.get("laughCount", 0) + stats.get("likeCount", 0) + stats.get("dislikeCount", 0) + stats.get("heartCount", 0) + stats.get("commentCount", 0)

if __name__ == "__main__":
    response = requests.get(
        f"{base_url}images",
        params=params,
        headers=headers
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        if response.status_code in errors_dict:
            print(errors_dict[response.status_code])
    else:
        images = response.json()["items"]
        first_image = images[0]
        print("First Image:\n")
        print(json.dumps(first_image, indent=4))
        meta = response.json()["metadata"]
        print("\nMeta Information:\n")
        print(json.dumps(meta, indent=4))