import os
import subprocess
import sys

def main():
    # Move to the src folder
    src_folder = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_folder)

    # Define pipeline scripts in execution order
    scripts = [
        'clean_jobs.py',
        'clean_resumes.py',
        'clean_courses.py',
        'baseline_model.py',
        'split_data.py',
        'build_features.py',
        'calculate_gaps.py',
        'recommend_courses.py',
        'evaluate.py'
    ]

    # Check required input files
    required_files = [
        '../data/raw/jobs.csv',
        '../data/raw/resumes.csv',
        '../data/raw/courses.csv',
        '../data/evaluation/human_labels.csv'
    ]

    # Stop if an input file is missing
    for file in required_files:
        if not os.path.exists(file):
            raise Exception(f'Missing required file: {file}')

    # Print pipeline information
    print('Starting CMPT 353 project pipeline')
    print('Working directory:', os.getcwd())
    print()

    # Run each script in order
    for script in scripts:
        print(f'Running {script}...')
        result = subprocess.run([sys.executable, script])

        # Stop immediately if one stage fails
        if result.returncode != 0:
            raise Exception(f'Pipeline stopped because {script} failed')

        print(f'{script} completed')
        print()

    # Print final output locations
    print('Pipeline completed successfully')
    print()
    print('Main outputs:')
    print('../outputs/tables/baseline_results.csv')
    print('../outputs/gaps/gap_results.csv')
    print('../outputs/recommendations/course_recommendations.csv')
    print('../outputs/evaluation/evaluation_results.csv')
    print()
    print('Run notebooks/analysis.ipynb separately '
          'for EDA, statistical analysis, figures, and findings.')


if __name__ == '__main__':
    main()
