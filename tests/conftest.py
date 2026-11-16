import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testsecretkey123changeme"
os.environ["AI_PROVIDER"] = "mock"
os.environ["PYTEST_CURRENT_TEST"] = "1"
