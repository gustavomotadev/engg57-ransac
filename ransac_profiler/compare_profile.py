import re

def percent_drop(soft, hard):
    soft = int(soft)
    hard = int(hard)
    #print(soft)
    #print(hard)
    #print(soft - hard)
    #print((soft - hard) / soft)
    #print()
    return float (-1 * 100 * ( (int(soft) - int(hard)) / int(soft)))

def my_format(s):
    s = list(s)
    for i in range(len(s)):
        if s[i] == '0' and i+1 < len(s) and s[i+1] != '.':
            s[i] = ' '
        else:
            break
    return ''.join(s)

def find(label, lista):
    i = 0
    for element in lista:
        if element[0] == label:
            return i
        i += 1
    return None

#Label: a | Section: FUN_COPY     | Executions:     2 | Mean:       156
padrao = re.compile(r'Label:\s+([a-z]).*Mean:\s+([0-9]+)')

label_dict = {
    'a': 'FUN_COPY', 
    'b': 'FUN_COMP', 
    'c': 'FUN_DSPL', 
    'd': 'FUN_LREG', 
    'e': 'FUN_DSPP',  
    'f': 'ALG', 
    'g': 'ITER', 
    'h': 'STEP_1', 
    'i': 'SELECT_2P',  
    'j': 'STEP_2', 
    'k': 'STEP_3',  
    'l': 'INLIER_CHECK',  
    'm': 'UPDATE_BEST', 
    'n': 'STEP_4', 
    'o': 'LREG_MED', 
    'p': 'LREG_SUM', 
    'q': 'LREG_RES' 
}

with open('tb_result_software_profile.txt', 'r') as software:
    dados_soft = software.readlines()

with open('tb_result_hardware_profile.txt', 'r') as hardware:
    dados_hard = hardware.readlines()

dados_soft = list(map(lambda x: re.search(padrao, x), dados_soft))
dados_hard = list(map(lambda x: re.search(padrao, x), dados_hard))

dados_soft = [(str(dado.groups()[0]), int(dado.groups()[1])) for dado in dados_soft if not dado is None and dado.groups()[0] != 'c']
dados_hard = [(str(dado.groups()[0]), int(dado.groups()[1])) for dado in dados_hard if not dado is None]

dados_soft.sort(key=lambda x: x[0])
dados_hard.sort(key=lambda x: x[0])

ordem_labels = []
for i, dado in enumerate(dados_soft):
    #print(dados_soft[i][0])
    #print(dados_hard[i][0])
    ordem_labels.append((dado[0], percent_drop(int(dados_soft[i][1]), int(dados_hard[i][1]))))
    #print()
ordem_labels.sort(reverse=True, key=lambda x: x[1])

#print(ordem_labels)

dados_soft.sort(key=lambda x: find(x[0], ordem_labels))
dados_hard.sort(key=lambda x: find(x[0], ordem_labels))

#print(dados_soft)
#print(dados_hard)

with open('comparation.txt', 'w') as output:

    for i in range(len(dados_soft)):

        print('| Label: ' + dados_soft[i][0] + ' | ' + '{:21s}'.format('Section: ' + label_dict[dados_soft[i][0]] + '') + 
        ' | Mean: ' + '{:9d}'.format(int(dados_hard[i][1]) - int(dados_soft[i][1])) + 
        ' | %: ' + my_format('{:7.3f}'.format(round(percent_drop(int(dados_soft[i][1]), int(dados_hard[i][1])), 6))) +
        ' | Factor: ' + my_format('{:7.3f}'.format(round(dados_soft[i][1]/dados_hard[i][1], 6))) + ' |') 

        output.write('| Label: ' + dados_soft[i][0] + ' | ' + '{:21s}'.format('Section: ' + label_dict[dados_soft[i][0]] + '') + 
        ' | Mean: ' + '{:9d}'.format(int(dados_hard[i][1]) - int(dados_soft[i][1])) + 
        ' | %: ' + my_format('{:7.3f}'.format(round(percent_drop(int(dados_soft[i][1]), int(dados_hard[i][1])), 6))) + ' |\n')