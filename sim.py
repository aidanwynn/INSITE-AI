import random
from numpy import mean
from scipy.stats import skewnorm
import numpy as np

def readCSV(fileName):
    True

def skewRand(loc=2.5):
    val = skewnorm.rvs(0, loc=loc, scale=1.2)
    val = round(val)    # round to nearest int
    if val > 5:
        val = 5
    if val < 0:
        val = 0
    return val

def skewIt(min, max, val, positive = True):
    """
        This function will pick a random number from 0-5, positively or negatively skewed based on val
    """
    median = 1
    x = val / (max - min)
    lower, upper = 0, 2.5
    a = lower + (upper - lower) * x
    if positive:
        a = median + a
    else:
        a = median - a
    val = skewnorm.rvs(0, loc=a, scale=1.2)
    val = round(val)    # round to nearest int
    if val > 5:
        val = 5
    if val < 0:
        val = 0
    
    return val

def _hyper_t(age, obesity):
    age_val = skewIt(5, 90, age, positive = True)
    obe_val = skewIt(0, 5, obesity, positive = True)
    val = round(mean([age_val, obe_val]))
    return val

def _diabetes(obesity):
    val = skewIt(0, 5, (obesity-2.5), positive = True)
    return val

def _cardio_v(hyper_t, diabetes):
    hyp_val = skewIt(0, 5, hyper_t-1, positive = True)
    dia_val = skewIt(0, 5, diabetes-1, positive = True)
    val = round(mean([hyp_val, dia_val]))
    return val

def _renal(hyper_t):
    val = skewIt(0, 5, (hyper_t-1), positive = True)
    return val

def _immuno_comp(age, diabetes):
    age_val = skewIt(5, 90, age, positive = True)
    dia_val = skewIt(0, 5, diabetes-1.5, positive = True)
    val = round(mean([age_val, dia_val]))
    return val

def vax_val():
    val = random.randint(0, 100)
    if val <= 75:
        return 1
    return 0

def _hospitalized(age,sex,vax,hyper_t,obesity,diabetes,lung_d,cardio_v,neuro_l,renal,immuno_comp,blood_d):
    age_val = (age-5)/(85)
    age_val = (age_val**4)
    
    if sex == 'M':
        sex_val = 0.55
    else:
        sex_val = 0.45
    
    if vax == 1:
        vax_v = 0.30
    else:
        vax_v = 0.70
    
    # %
    ageW = 17
    sexW = 3
    vaxW = 16
    hyper_tW = 14
    obesityW = 10
    diabetesW = 9
    lung_dW = 6
    cardio_vW = 5
    neuro_lW = 2
    renalW = 2
    immuno_compW = 14
    blood_dW = 2

    weightSum = ageW+sexW+vaxW+hyper_tW+obesityW+diabetesW+lung_dW+cardio_vW+neuro_lW+renalW+immuno_compW+blood_dW
    
    val = ((age_val)*ageW + (sex_val)*sexW + (vax_v)*vaxW + (hyper_t/5)*hyper_tW + (obesity/5)*obesityW + (diabetes/5)*diabetesW + (lung_d/5)*lung_dW + (cardio_v/5)*cardio_vW + (neuro_l/5)*neuro_lW + (renal/5)*renalW + (immuno_comp/5)*immuno_compW + (blood_d/5)*blood_dW) / weightSum
    
    if val >= 0.4:
        val = True
    else:
        val = False
    return val

def generateHealthDataset(num, fileName):
    file = open(fileName, 'w+')
    file.write("age,sex,vax,hyper_t,obesity,diabetes,lung_d,cardio_v,neuro_l,renal,immuno_comp,blood_d,hospitalized")
    # All values are from 0-5, min-max. Hospitalized is boolean (0/1)

    print("Generating "+ str(num) +" data points...")
    for i in range(num):
        age = round(random.uniform(5, 90))
        list = ['M','F']
        sex = random.choice(list)
        vax = vax_val()
        obesity = round(random.uniform(0, 5))
        hyper_t = _hyper_t(age, obesity)
        diabetes = _diabetes(obesity)
        lung_d = skewRand(loc=0)
        cardio_v = _cardio_v(hyper_t, diabetes)
        neuro_l = skewRand(loc=-1)
        renal = _renal(hyper_t)
        immuno_comp = _immuno_comp(age, diabetes)
        blood_d = skewRand(loc=-1.5)
        hospitalized = _hospitalized(age,sex,vax,hyper_t,obesity,diabetes,lung_d,cardio_v,neuro_l,renal,immuno_comp,blood_d)
        
        file.write(     '\n'+str(age)+","+sex+","+str(vax)+","+str(hyper_t)+","+str(obesity)+","+str(diabetes)+","
                        +str(lung_d)+","+str(cardio_v)+","+str(neuro_l)+","+str(renal)+","
                        +str(immuno_comp)+","+str(blood_d)+","+str(hospitalized))
        
    print("Generation complete.")
    file.close()
    print("Output file saved to: '"+ fileName +"'")

if __name__ == "__main__":
    fileName = 'data.csv'
    generateHealthDataset(10000, fileName)
    
