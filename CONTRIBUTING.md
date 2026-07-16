# Contributing Guidelines

Thank you for your interest in contributing to the Smart Face Attendance System! We welcome contributions from the community to help improve the system, add new features, and fix bugs.

## How Can You Contribute?

### 1. Reporting Bugs
If you find a bug, please create an Issue on the repository. Include:
- A clear, descriptive title.
- Steps to reproduce the bug.
- Expected behavior vs. actual behavior.
- Screenshots if applicable.
- Your OS, browser version, and Python version.

### 2. Suggesting Enhancements
Have an idea for a new feature? We'd love to hear it! Create an Issue describing:
- What the feature is.
- Why it would be useful.
- How you envision it working.

### 3. Submitting Pull Requests (Code Contributions)
If you want to write code, please follow these steps:

1. **Fork the Repository:** Create your own fork of the project.
2. **Create a Branch:** Create a new branch for your feature or bugfix (`git checkout -b feature/amazing-feature` or `git checkout -b fix/annoying-bug`).
3. **Write Code:** Implement your changes.
    - Ensure your code follows the existing style (e.g., standard PEP 8 for Python).
    - If you are modifying the UI, ensure you adhere to the glassmorphic design system outlined in `style.css`.
4. **Test:** Run the application locally and verify your changes don't break existing functionality (especially the camera feed and ML pipeline).
5. **Commit & Push:** Commit your changes with clear, descriptive commit messages.
6. **Open a PR:** Open a Pull Request against the `main` branch of the original repository. Describe your changes in detail in the PR description.

## Development Setup

To set up your local development environment:

1. Ensure you have Python 3.10+ installed.
2. Clone the repository and navigate into it.
3. Create a virtual environment: `python -m venv venv`
4. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run the server: `python app.py`

## Code of Conduct
Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. Be respectful, constructive, and inclusive.

Happy coding! 🚀
