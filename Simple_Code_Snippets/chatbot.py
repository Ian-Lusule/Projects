import os
import json
import logging
import random

from rasa.nlu.training_data import TrainingData, Message
from rasa.nlu.components import ComponentBuilder
from rasa.nlu import config
from rasa.nlu.model import Trainer, Interpreter
from rasa.core.agent import Agent
from rasa.core.policies import MemoizationPolicy, RulePolicy, TEDPolicy
from rasa.core.domain import Domain
from rasa.core.training import interactive
from rasa.core.utils import EndpointConfig
from rasa.utils.endpoints import ClientResponseError

from rasa.nlu.config import RasaNLUModelConfig
from rasa.core.config import load as load_core_config

# Constants
NLU_MODEL_PATH = "models/nlu"
CORE_MODEL_PATH = "models/core"
NLU_DATA_PATH = "data/nlu.md"
CORE_DOMAIN_PATH = "domain.yml"
CORE_STORIES_PATH = "data/stories.md"
CORE_CONFIG_PATH = "config.yml"
ENDPOINTS_PATH = "endpoints.yml"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chatbot:
    def __init__(self):
        self.nlu_interpreter = None
        self.agent = None
        self.domain = None

    def train_nlu(self):
        """Trains the NLU model using Rasa NLU."""
        try:
            training_data = TrainingData.load(NLU_DATA_PATH)
            configuration = config.load("config.yml")  #  NLU config
            trainer = Trainer(configuration)
            trainer.train(training_data)
            model_directory = trainer.persist(path=NLU_MODEL_PATH, fixed_model_name="nlu")

            logger.info(f"NLU model trained and saved to {model_directory}")
            return model_directory
        except Exception as e:
            logger.error(f"Error during NLU training: {e}")
            return None

    def train_core(self):
        """Trains the Core model using Rasa Core."""
        try:
            domain = Domain.load(CORE_DOMAIN_PATH)
            self.domain = domain
            agent = Agent(
                domain,
                policies=[MemoizationPolicy(), RulePolicy(), TEDPolicy(max_history=5, epochs=200)]
            )
            agent.train(
                CORE_STORIES_PATH,
                domain,
                epochs=300,
                batch_size=50,
                augmentation_factor=20,
                validation_split=0.2
            )
            agent.persist(CORE_MODEL_PATH)
            self.agent = agent
            logger.info(f"Core model trained and saved to {CORE_MODEL_PATH}")
            return agent
        except Exception as e:
            logger.error(f"Error during Core training: {e}")
            return None

    def load_models(self):
        """Loads the trained NLU and Core models."""
        try:
            self.nlu_interpreter = Interpreter.load(os.path.join(NLU_MODEL_PATH, "nlu"))
            self.agent = Agent.load(CORE_MODEL_PATH)
            self.domain = Domain.load(CORE_DOMAIN_PATH)
            logger.info("NLU and Core models loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

    def run_interactive_training(self):
        """Runs interactive training for Rasa Core."""
        try:
            endpoints = EndpointConfig.from_yaml_path(ENDPOINTS_PATH)
            interactive.run_interactive_learning(
                agent=self.agent,
                stories_file=CORE_STORIES_PATH,
                domain_file=CORE_DOMAIN_PATH,
                endpoints=endpoints
            )
            logger.info("Interactive training completed.")
        except Exception as e:
            logger.error(f"Error during interactive training: {e}")

    def handle_message(self, message):
        """Handles a user message and returns the chatbot's response."""
        try:
            if not self.nlu_interpreter or not self.agent:
                logger.error("NLU or Core models not loaded. Please train and load the models first.")
                return "I'm sorry, I'm not ready yet. Please try again later."

            results = self.nlu_interpreter.parse(message)
            logger.debug(f"NLU Parsing Results: {results}")

            action_results = self.agent.handle_text(message)
            logger.debug(f"Core Action Results: {action_results}")

            if action_results:
              responses = []
              for result in action_results:
                  if "text" in result:
                      responses.append(result["text"])
              return " ".join(responses)

            else:
                return "I'm not sure I understand. Could you rephrase that?"

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return "I'm having trouble understanding. Please try again."


    def run(self):
        """Runs the chatbot in a loop."""
        print("Chatbot is running. Type 'stop' to end the conversation.")
        while True:
            user_message = input("You: ")
            if user_message.lower() == "stop":
                print("Chatbot stopped.")
                break
            response = self.handle_message(user_message)
            print(f"Chatbot: {response}")

# Example Usage (Train, Load, and Run)
if __name__ == "__main__":
    chatbot = Chatbot()

    # Train NLU and Core models (optional - only if you've made changes)
    train_new_models = False  # Set to True to retrain.  Training takes time.
    if train_new_models:
        chatbot.train_nlu()
        chatbot.train_core()

    # Load pre-trained models
    if chatbot.load_models():
        # Run the chatbot
        chatbot.run()
    else:
        print("Failed to load models. Please check the logs for errors.")