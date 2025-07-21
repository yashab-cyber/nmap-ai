"""
AI Script Generation Example for NMAP-AI.

This example demonstrates how to use NMAP-AI's AI-powered script generation
to create custom Nmap scripts based on your specific requirements.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nmap_ai.ai.script_generator import AIScriptGenerator
from nmap_ai.config import Config
from nmap_ai.utils.logger import get_logger


def main():
    """Main function for AI script generation example."""
    parser = argparse.ArgumentParser(description="AI Script Generation Example")
    parser.add_argument("--service", required=True, help="Target service (ssh, http, ftp, etc.)")
    parser.add_argument("--description", required=True, help="Describe what you want to detect")
    parser.add_argument("--output", "-o", help="Output file for generated script")
    parser.add_argument("--security-focus", action="store_true", help="Focus on security vulnerabilities")
    parser.add_argument("--performance-focus", action="store_true", help="Focus on performance analysis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = get_logger("ai_script_example", level="DEBUG" if args.verbose else "INFO")
    
    try:
        # Initialize configuration
        config = Config()
        
        # Create AI script generator
        logger.info("Initializing AI Script Generator...")
        generator = AIScriptGenerator(config)
        
        # Generate script
        logger.info(f"Generating script for {args.service} service")
        logger.info(f"Description: {args.description}")
        
        script_config = {
            'security_focus': args.security_focus,
            'performance_focus': args.performance_focus,
            'target_service': args.service,
            'verbose': args.verbose
        }
        
        generated_script = generator.generate_script(
            target_service=args.service,
            description=args.description,
            **script_config
        )
        
        if not generated_script:
            logger.error("Failed to generate script")
            sys.exit(1)
        
        # Display results
        print("\n" + "="*60)
        print("GENERATED NMAP SCRIPT")
        print("="*60)
        print(generated_script)
        print("="*60)
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(generated_script)
            logger.info(f"Script saved to {output_path}")
        
        # Show usage example
        print(f"\nUsage Example:")
        print(f"nmap --script-args '{args.service}-custom.arg1=value1' --script {args.service}-custom.nse <target>")
        
        # Get confidence score
        confidence = generator.get_generation_confidence()
        if confidence:
            print(f"\nGeneration Confidence: {confidence:.2f}/1.0")
        
        logger.info("Script generation completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Script generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def demonstrate_predefined_scripts():
    """Demonstrate generation of predefined script types."""
    print("\n" + "="*60)
    print("PREDEFINED SCRIPT EXAMPLES")
    print("="*60)
    
    config = Config()
    generator = AIScriptGenerator(config)
    
    examples = [
        {
            'service': 'ssh',
            'description': 'Detect SSH misconfigurations and weak ciphers',
            'security_focus': True
        },
        {
            'service': 'http',
            'description': 'Find common web vulnerabilities and misconfigurations',
            'security_focus': True
        },
        {
            'service': 'ftp',
            'description': 'Check for anonymous FTP access and banner information',
            'security_focus': False
        },
        {
            'service': 'smtp',
            'description': 'Enumerate SMTP users and check for open relays',
            'security_focus': True
        }
    ]
    
    for example in examples:
        print(f"\n--- {example['service'].upper()} Script ---")
        print(f"Description: {example['description']}")
        
        try:
            script = generator.generate_script(
                target_service=example['service'],
                description=example['description'],
                security_focus=example['security_focus']
            )
            
            if script:
                # Show just the first few lines
                lines = script.split('\n')
                for line in lines[:10]:
                    print(f"  {line}")
                if len(lines) > 10:
                    print(f"  ... ({len(lines) - 10} more lines)")
                    
        except Exception as e:
            print(f"  Error generating script: {e}")


def interactive_mode():
    """Interactive script generation mode."""
    print("\n" + "="*60)
    print("INTERACTIVE SCRIPT GENERATION")
    print("="*60)
    print("Enter 'quit' to exit interactive mode")
    
    config = Config()
    generator = AIScriptGenerator(config)
    
    while True:
        try:
            # Get user input
            service = input("\nTarget Service (ssh/http/ftp/smtp/etc): ").strip()
            if service.lower() == 'quit':
                break
                
            if not service:
                print("Please enter a service name")
                continue
            
            description = input("What do you want to detect/analyze? ").strip()
            if not description:
                print("Please enter a description")
                continue
            
            security_focus = input("Security focus? (y/N): ").strip().lower().startswith('y')
            
            print(f"\nGenerating script for {service}...")
            
            # Generate script
            script = generator.generate_script(
                target_service=service,
                description=description,
                security_focus=security_focus
            )
            
            if script:
                print(f"\nGenerated Script:")
                print("-" * 40)
                print(script)
                print("-" * 40)
                
                # Ask if user wants to save
                save = input("\nSave script to file? (y/N): ").strip().lower().startswith('y')
                if save:
                    filename = input("Enter filename (without extension): ").strip()
                    if filename:
                        filepath = Path(f"{filename}.nse")
                        filepath.write_text(script)
                        print(f"Script saved to {filepath}")
            else:
                print("Failed to generate script. Please try again.")
                
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("NMAP-AI Script Generation Examples")
        print("=" * 40)
        print("\nOptions:")
        print("1. Command line script generation")
        print("2. View predefined examples")
        print("3. Interactive mode")
        print("\nExamples:")
        print("python ai_script_gen.py --service ssh --description 'Check for weak SSH configurations'")
        print("python ai_script_gen.py --service http --description 'Find XSS vulnerabilities' --security-focus")
        
        choice = input("\nChoose an option (1-3): ").strip()
        
        if choice == "1":
            print("Use --help for command line options")
        elif choice == "2":
            demonstrate_predefined_scripts()
        elif choice == "3":
            interactive_mode()
        else:
            print("Invalid choice")
    else:
        main()
