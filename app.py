# Local Application Imports
from modules.config import initialize_directories
from modules.logging_config import configure_logging
from interface.main_app import main_app

def run():
    # Initialize the project directories
    project_root, cache_dir, fonts_dir, output_dir = initialize_directories()

    # Configure logging based on the verbose flag
    configure_logging(verbose=False)

    # Launch the main application
    app = main_app(cache_dir, fonts_dir, output_dir, project_root)
    app.launch()

if __name__ == "__main__":
    run()