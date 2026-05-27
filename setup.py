"""
Setup configuration for Bookfix - Ebook Text Processor
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys


class PostInstallCommand(install):
    """Post-installation command to download spaCy language model."""

    def run(self):
        """Run the standard install, then download spaCy model."""
        install.run(self)

        print("\n" + "="*70)
        print("Installing spaCy language model (en_core_web_md)...")
        print("="*70 + "\n")

        try:
            subprocess.check_call([
                sys.executable, '-m', 'spacy', 'download', 'en_core_web_md'
            ])
            print("\n" + "="*70)
            print("✓ spaCy model installed successfully!")
            print("="*70 + "\n")
        except subprocess.CalledProcessError as e:
            print("\n" + "="*70)
            print(f"⚠ Warning: Failed to install spaCy model: {e}")
            print("You can manually install it with:")
            print("  python -m spacy download en_core_web_md")
            print("="*70 + "\n")


setup(
    name='bookfix',
    version='1.0.0',
    description='Ebook text processor for TTS preparation',
    author='Bookfix Project',
    python_requires='>=3.10',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.14.2',
        'g2p_en==2.1.0',
        'matplotlib==3.10.7',
        'nltk==3.9.2',
        'num2words==0.5.14',
        'numpy==2.3.4',
        'pandas==2.3.3',
        'pygame==2.6.1',
        'PyQt5==5.15.11',
        'PyQt5_sip==12.17.0',
        'Requests==2.32.5',
        'spacy==3.8.7',
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'bookfix=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
