import base64
from github import Github
from github import InputGitTreeElement

token = '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'
g = Github(token)
repo = g.get_user().get_repo('koncert_test') # repo name
filepath = 'C:/Users/Urban/Documents/Fakulteta za elektrotehniko/BMA 2. Semester/Avtomatizirani_In_Virtualni_Merilni_Sistemi/AVMS Projekt/test'

data = open(filepath).read()
element = InputGitTreeElement(filepath,'100644', 'blob', data)

master_ref = repo.get_git_ref('heads/master')
master_sha = master_ref.object.sha
base_tree = repo.get_git_tree(master_sha)
tree = repo.create_git_tree(element, base_tree)
parent = repo.get_git_commit(master_sha)
commit = repo.create_git_commit('test', tree, [parent])
master_ref.edit(commit.sha)