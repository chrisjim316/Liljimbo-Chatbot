from wit import Wit

access_token = "HASFWGKV2HBFHTI6MXYSGI7HLZHVC7XN"

client = Wit(access_token = access_token)

message_text = "sdfg is not a location"

resp = client.message(message_text)

print(resp)
