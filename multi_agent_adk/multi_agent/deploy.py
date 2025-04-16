import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
import agent

PROJECT_ID = "hasanrafiq-test-331814"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://hasanrafiq-test-331814"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

app = reasoning_engines.AdkApp(
    agent = agent.root_agent,
    enable_tracing=True,
)

remote_app = agent_engines.create(
    agent_engine=agent.root_agent,
    extra_packages = ["agent.py"],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"   
    ]
)

# Test ( Local )
# session = app.create_session(user_id="u_123")
# print(session)

# for event in app.stream_query(
#     user_id="u_123",
#     session_id=session.id,
#     message="whats the weather in new york",
# ):
#     print(event)