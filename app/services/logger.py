import logging

# Configure the logger instance
logging.basicConfig(level=logging.DEBUG, filename='app.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# Export logger instance
logger = logging.getLogger("phishing_protector")
