from git import Repo

repo_dir = 'mathematics'
repo = Repo(repo_dir)
file_list = [
    'numerical_analysis/regression_analysis/simple_regression_analysis.py',
    'numerical_analysis/regression_analysis/simple_regression_analysis.png'
]
commit_message = 'Add simple regression analysis'
repo.index.add(file_list)
repo.index.commit(commit_message)
origin = repo.remote('origin')
origin.push()