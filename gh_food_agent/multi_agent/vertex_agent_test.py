from vertexai import agent_engines

agent_deployed = list(agent_engines.list())[-1]

for event in agent_deployed.stream_query(
    user_id="u_123",
    message="whats the weather in new york",
    # input={"messages": [
    # ("user", "What is the exchange rate from US dollars to Swedish currency?")
    # ]}
    ):

    print(event)