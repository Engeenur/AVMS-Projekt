from git import Repo

repo_dir = 'C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt'
repo = Repo(repo_dir)
filepath = 'C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Measurements\\test_meritev'
commit_message = 'Test avtomatskega nalaganja na git'
repo.index.add(filepath)
repo.index.commit(commit_message)
origin = repo.remote('origin')
origin.push()