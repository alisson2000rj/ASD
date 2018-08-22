import os
def apaga_resultados():
  path = "./resultados/"
  dir = os.listdir(path)
  for file in dir:
    os.remove(path+file)

apaga_resultados()
os.system("python3 c-fork.py &")
os.system("python3 c-fork.py &")
