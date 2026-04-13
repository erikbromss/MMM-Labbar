import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "models"))
 
import numpy as np
import matplotlib.pyplot as plt
 
from utils import load_emissions, load_radiative_forcing, to_ppm
from models.biosphere_and_oceans import combined_ocean_biosphere
from models.energy_balance import rf
from task9 import other_aerosol_total_rf
from task10 import energybalance

# =================================================

# Parametrar: De bästa vi fick för lambda = 0.8
# var kappa = 1, s = 1. Kunde ju testat fler värden för ännu bättre fit
# säkert men nu gör vi så här. 

LAM = 0.8
K = 1
S = 1

# Referensperiod - samma som NASA
ref_start = 1951
ref_end = 1980

# modellens tidsgränser 
hist_start = 1765
hist_end = 2024
future_end = 2200

# ===================================================
# LADDA DATA
# ===================================================

years, emissions = load_emissions()

hist_years = [y for y in years if hist_start <= y <= hist_end]
hist_emissions = emissions[:len(hist_years)]

rfdf = load_radiative_forcing()

rf_other_full = other_aerosol_total_rf(rfdf, S)
rf_other_years = rfdf['Time (year)'].tolist()

def get_rf_other(year_list):
    """Plockar ut rf_other för en given lista av år"""
    idx = [rf_other_years.index(y) for y in year_list]
    return np.array([rf_other_full[i] for i in idx])


# ===================================================
# Bygg upp olika utsläpps-scenarios
# ===================================================

emission_2024 = 10.59522 #hämtat ur utsläppCSV direkt

future_years = list(range(hist_end + 1, future_end + 1)) # 2025-2200
n_future = len(future_years)

def build_scenario(future_years, emission_2024):
    """Returnerar de tre utsläppscenarios som arrays med koncentrationsnivåer"""

    n = len(future_years)
    
    s1 = np.zeros(n) #scenario 1: linjär minskning -> noll -> negativ -> konstant
    s2 = np.zeros(n) #scenario 2: konstant
    s3 = np.zeros(n) #scenario 3: linjär ökning -> konstant

    idx_2070 = future_years.index(2070) # noll utsläpp då i scenario 1 
    idx_2100 = future_years.index(2100) # tak scenario 3, konstant scenario 1 

    rate1 = emission_2024 / (2070 - hist_end) # linkär minskning
    rate3 = emission_2024 / (2100 - hist_end)

    for j, y in enumerate(future_years):

        #scenario 1:
        if y <= 2070:
            s1[j] = emission_2024 - rate1 * (y - hist_end)
        elif y <= 2100:
            s1[j] = - rate1 * (y-2070)
        else:
            #konstant post 2100
            s1[j] = s1[future_years.index(2100)]
        
        # --- Scenario ii ---
        s2[j] = emission_2024
 
        # --- Scenario iii ---
        if y <= 2100:
            s3[j] = emission_2024 + rate3 * (y - hist_end)
        else:
            s3[j] = 2 * emission_2024
 
    return s1, s2, s3
 
s1, s2, s3 = build_scenario(future_years, emission_2024)



def run_scenario(hist_years, hist_emissions, future_years, future_emissions, lam = 0.8, k = 0.5, s = 1):
    """
    Kör combined_ocean_biosphere och energybalance för hela perioden
    1765 → FUTURE_END.
 
    Returns:
        all_years, dT1_adj
    """
    all_years = hist_years + future_years
    all_emissions = list(hist_emissions) + list(future_emissions)
 
    # Kolcykelmodell
    m_atm, _, _ = combined_ocean_biosphere(all_years, all_emissions)
    konc = to_ppm(m_atm) 
 
    # Radiativ forcing CO2
    rf_co2 = np.array([rf(c) for c in konc])
 
    rf_other = get_rf_other(all_years) * s
 
    rf_total = rf_co2 + rf_other
 
    # Energibalansmodell
    dT1, _ = energybalance(rf_total, lam=lam, k=k)
    dT1 = np.array(dT1[1:])  # trimma startvärde
 
    # Justera relativt referensperioden 1951–1980
    ref_s = all_years.index(ref_start)
    ref_e = all_years.index(ref_end)
    dT1_adj = dT1 - np.mean(dT1[ref_s : ref_e + 1])
 
    return all_years, dT1_adj

years1, dT1_1 = run_scenario(hist_years, hist_emissions, future_years, s1)
years2, dT1_2 = run_scenario(hist_years, hist_emissions, future_years, s2)
years3, dT1_3 = run_scenario(hist_years, hist_emissions, future_years, s3)

# =====================================================
# Plotta utsläpps-scenarios samt temperaturprojektioner
# över (1765 - 2100)
# =====================================================

fig, axs = plt.subplots(1, 2, figsize = (14, 5))

# kör utsläpp i vänster plot
axs[0].plot(hist_years, [emission_2024] * len(hist_years), color = 'gray', linewidth = '0.8', linestyle = 'dashed', label = 'Historiska Usläpp (konstant ref.)')
axs[0].plot(future_years, s1, color = 'steelblue', label = 'Scenario 1')
axs[0].plot(future_years, s2, color = 'darkorange', label = 'Scenario 2')
axs[0].plot(future_years, s3, color = 'firebrick', label = 'Scenario 3')
axs[0].axhline(0, color = 'black', linewidth = 0.5, linestyle = '--')
axs[0].set_xlabel('År')
axs[0].set_ylabel('CO₂-utsläpp (GtC/år)')
axs[0].set_title('Utsläppsscenarier 2025-2200')
axs[0].legend(fontsize=8)
axs[0].grid(True, alpha=0.4)

# kör temperatur i höger plot 

axs[1].plot(years1, dT1_1, color = 'steelblue', label = 'Scenario 1')
axs[1].plot(years2, dT1_2, color = 'darkorange', label = 'Scenario 2')
axs[1].plot(years3, dT1_3, color = 'firebrick', label = 'Scenario 3')
axs[1].axhline(1.5, color='black', linewidth=0.8, linestyle='--', label='1.5°C (Paris)')
axs[1].axhline(2.0, color='black', linewidth=0.8, linestyle=':',  label='2.0°C (Paris)')
axs[1].axvline(2100, color='gray', linewidth=0.6, linestyle='--')
axs[1].set_xlabel('År')
axs[1].set_ylabel('Temperaturanomali (°C, relativt 1951–1980)')
axs[1].set_title('Temperaturprojektioner 1765–2200 (λ=0.8)')
axs[1].legend(fontsize=8)
axs[1].grid(True, alpha=0.4)

plt.suptitle('12a): C02-scenarerier och temperaturprojektioner')
plt.tight_layout()
plt.show()

# skriv ut tempen år 2100 för varje scenario
for name, ys, dT in [('1', years1, dT1_1), ('2', years2, dT1_2), ('3', years3, dT1_3)]:
    idx2100 = ys.index(2100)
    print(f'Scenario {name}: dT år 2100 = {dT[idx2100]:.2f} grader Celsius')

# =================================================
# 12b): Exakt samma plot som 12a) bara att vi justerar
# "nollpunkten" från 1951-1980 -> 1765 - 1800
# =================================================


def preindustrial_adj(all_years, dT1_adj):
    idx_s = all_years.index(1765)
    idx_e = all_years.index(1800)
    preindustrial_mean = np.mean(dT1_adj[idx_s : idx_e + 1])
    return dT1_adj - preindustrial_mean

dt1pi = preindustrial_adj(years1, dT1_1)
dt2pi = preindustrial_adj(years2, dT1_2)
dt3pi = preindustrial_adj(years3, dT1_3)

for name, ys, dt in [('1',   years1,   dt1pi), ('2',  years2,  dt2pi), ('3', years3, dt3pi)]:
    idx2100 = ys.index(2100)
    print(f'Scenario {name}: dT år 2100 = {dt[idx2100]:.2f} Celsius (relativt pre-industriellt)')

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(years1, dt1pi, color = 'Steelblue', label = 'Scenario 1')
ax.plot(years2, dt2pi, color = 'darkorange', label = 'Scenario 2')
ax.plot(years3, dt3pi, color = 'firebrick', label = 'Scenario 3')

ax.axhline(1.5, color = 'black', linewidth = 0.8, linestyle = '--', label = '1.5 grader Celsius / År (Paris)')
ax.axhline(2, color = 'black', linewidth = 0.8, linestyle = ':', label = '2.0 grader Celsius / År (Paris)')

for ys, dt, color in [(years1,   dt1pi,   'steelblue'), (years2,  dt2pi,  'darkorange'), (years3, dt3pi, 'firebrick')]:
    idx = ys.index(2100)
    ax.scatter(2100, dt[idx], color = color, zorder = 5, s = 60)
    ax.annotate(f'{dt[idx]:.2f}°C', xy = (2100, dt[idx]), xytext = (8,0), textcoords = 'offset points', fontsize = 8, color = color)

ax.axvline(2100, color = 'gray', linewidth = 0.6, ls = '--')
ax.set_xlim(1765, 2200)
ax.set_xlabel('År')
ax.set_ylabel('Temperaturökning (°C)')
ax.set_title('12b): Temperaturökning relativt pre-industriell nivå')
ax.legend()
ax.grid(True, alpha = 0.5)
plt.tight_layout()
plt.show()

# ==============================================
# 12c) Bygg upp scenario 1-3 för varje bästa uppstättning
# av parametrar (lambda, kappa, s) och ta reda på 
# min, max och medium temperaturer för alla dessa, 
# spara och plotta i samma plot
# ==============================================

# bästa parameterkombinationerna av de värden man körde i task 11, igen hade säkert kunnat prova fler för att få ännu bättre fit
param_sets = {0.5: {'k': 0.2, 's': 1}, 
              0.8: {'k': 1, 's': 1}, 
              1.3: {'k': 1, 's': 1}}

scenarios = {'1':   (future_years, s1), 
             '2':  (future_years, s2), 
             '3': (future_years, s3),}


colors = {'1': 'steelblue', '2': 'darkorange', '3': 'firebrick'}

fig, ax = plt.subplots(figsize=(10, 5))

for scen, (fut_years, fut_emissions) in scenarios.items():

    temp = [] # för varje scenario, samla en temp-kurva per lambda

    for lam, params in param_sets.items():
        
        # sätt in lambda, kappa, s i argument för yttre funktion så de ändras i anropet för energybalance inuti funktionen 
        ys, dT = run_scenario(hist_years, hist_emissions, fut_years, fut_emissions, lam = lam, k = params['k'], s = params['s'])
        dTpi = preindustrial_adj(ys, dT) # sätt referens -> pre indsustrial-temperaturer, inte mean(1951-1980)

        temp.append(dTpi)
    
    # Claude Band plot: 
    lower = np.minimum.reduce(temp) # ger ny array där varje element är det minsta värdet bland de tre kurvorna vid det årtalet. 
    upper = np.maximum.reduce(temp) # motsvarande för maximum, ger tsm under och överkurvor som vid varje tid representerar det lägsta respektive högsta temperaturprojektionerna över alla lambda vi kört. 
    mid = temp[1] #lambda 0.8

    ax.fill_between(ys, lower, upper, alpha = 0.25, color = colors[scen]) # fyll i osäkerhetsbanden för varje scenario genom att skugga mellan upper - lower i motsvarande scenarios färg. 
    ax.plot(ys, mid, color = colors[scen], label = f'Scenario {scen} (λ=0.8)')
    ax.plot(ys, lower, color = colors[scen], linewidth = 0.6, linestyle = '--')
    ax.plot(ys, upper, color = colors[scen], linewidth = 0.6, linestyle = '--')

ax.axhline(1.5, color='black', linewidth=0.8, linestyle='--', label='1.5°C')
ax.axhline(2.0, color='black', linewidth=0.8, linestyle=':',  label='2.0°C')
ax.axvline(2100, color='gray', linewidth=0.6, linestyle='--')
ax.set_xlabel('År')
ax.set_ylabel('Temperaturökning (°C, relativt pre-industriellt)')
ax.set_title('Task 12c: Temperaturspridning år 2100 givet osäkerhet i λ')
ax.legend()
ax.grid(True, alpha=0.5)
plt.tight_layout()
plt.show()


# Analysis - exempel: 
# Scenario 1 (minskning): 0.8°C – 1.4°C
# Scenario 2 (konstant):  2.1°C – 3.2°C  
# Scenario 3 (ökning):    3.5°C – 5.1°C

# Inget överlapp mellan temperaturintervall´, t1 < t2 < t3. 
# Utsläppsscenariot spelar större roll för temperaturen än osäkerheten i lambda. 
# Klimatpolitiken vi för har större påverkan på framtida MGSTI:er
# än det faktum att vi inte känner till lambda exakt. 
# Omvänt: kraftigt överlapp mellan banden <-> finns lambdavärden
# där scenarier ger ungefär samma MGSTI. 
# Dvs osäkerheten i lambda är så stor att vi inte ens kan säga 
# definitivt att utsläppsminskningar hjälper tillräckligt 
# för att nå under exempelvis 2*C. Osäkerheten i klimatsystemet dominerar
# alltså då över valet av utsläppsscenario. 


# =======================================
# 12d) diskussion utifrån texter
# ======================================

# Resultaten från våra simuleringar visar tydligt hur avgörande klimatkänsligheten lambda
# är för framtidens temperaturutveckling. Genom att variera lambda mellan 0.5 och 1.3 K/(W/m²)
# ser vi att samma utsläppsscenario kan leda till fundamentalt olika utfall – från en hanterbar 
# uppvärmning till att vi med råge överskrider Parisavtalets 2-gradersmål långt före seklets slut
# som grafiken producerad i 12c) visar. Denna vetenskapliga osäkerhet är självfallet en stor utmaning
# för politiker och beslutsfattare i globala klimatfrågor. Frågan blir hur vi som individer, grupper, nationer och
# människor bör agera, när vi inte vet hur känsligt systemet egentligen är. 

# Ur ett hållbarhetsperspektiv, som diskuteras av Lundqvist, är försiktighetsprincipen viktig att ha i åtanke. 
# Eftersom vi riskerar irreversibla skador på planetens ekologiska stödsystem om temperaturen stiger för högt, 
# bör osäkerhet inte vara ett argument för passivitet, från vår sida. Snarare tvärtom: om det finns en betydande 
# risk att klimatkänsligheten ligger i det övre spannet, typ lambda = 1.3, krävs kraftiga utsläppsminskningar 
# redan nu som en form av "försäkring". Konjunkturrådet (2020) har ett liknande perspektiv på risk. 
# Att vänta på "perfekt" kunskap om klimatkänsligheten - att stå som passiv observerare tills dess
# vi har mer information om lambda (samt även kappa) - vore ekonomiskt och ekologiskt oförsvarsbart. 
# Kostnaden att i framtiden behöva abbrupt panikbromsa temperaturökningen, till följd av ovannämnd passivitet, 
# är sannolikt högre än kostnaden för en planerad omställning med start idag. 

# I botten av klimatfrågan vilar grundetiken om att bevara planeten för eftervärlden, 
# att förvalta den jord vi lever på för framtida generationer - (Se Michael Jackson: Earth song ;) )
# I samma anda är det då värt att belysa denna intergenerationella rättvisa. 
# Om vi optmistiskt skulle utgå från ett lågt lambda - och ha fel - ja, 
# då berövar vi framtida generationer att nå globala mål för hållbar utveckling. 
# Enligt Lundqvist är ekologin grundförutsättningen för den sociala och ekonomiska
# sidan av denna debatt; utan ett stabilt klimat hotas allt, inte minst välfärd, levnadskvalité 
# och global hälsa. Det finns merit till detta förhållningssätt men även omvändningen tål att begrundas: 
# om ekologisk preservation inslussas på stor bekostnad av majoritetbefolkningens allmäna välstånd, 
# hur mycket ska människan behöva offra av det liv hon känner till, för att ge liv åt henne som kommer efter? 
# Ty vad är ett eländigt liv, annat än elände? Och vad är meningen med att leva ett sådant, 
# om det inte erbjuder möjlighet till självförverkligande? 


# Konjunkturrådet argumenterar vidare för att svensk politik bör fokusra på global klimatnytta, 
# snarare än något på mindre skala. Vi ska alltså inte bara minska våra egna utsläpp 
# i den mån det är socialt och ekonomiskt försvarsbart, utan också satsa på teknikutveckling
# som kan sänka kostnaden för att även andra nationer kan ställa om. Det kan handla om utveckling av grön transport
# och subventionering av denna så att människor lättare kan lämna sina fossildrivna transportmedel för de 
# nya grönare alternativen.
# Fokus ligger alltså på att sänka kostnadströskeln för att andra länder ska ställa om. 
# Givet osäkerheten i hur snabbt temperaturen stiger, blir förmågan att skala upp 
# sådana tekniska lösningar en viktig säkerhetsmarginal. Vi borde anta det värsta snarare än det bästa
# för att se till att det handlingsutrymme vi fortfarande har till att påverka och bromsa antropogen klimatpåverkan
# faktiskt räcker till för att hålla oss under ex. 2-graders-nivån från parisavtalet. 

# Sammanfattningsvis bör osäkerheten i parametrar som lambda, kappa och s leda till en mer ambitiös klimatpolitik,
# inte en mindre. För att med hög sannolikhet uppfylla Parisavtalet krävs att vi planerar 
# för ett scenario där klimatkänsligheten är hög. Genom att integrera försiktighetsprincipen
# med ekonomiska styrmedel som främjar global teknikspridning kan vi skapa en strategi som håller även om våra modeller visar sig vara i underkant. 
# Att reducera utsläppen kraftigt under de kommande decennierna är det enda sättet att bibehålla handlingsutrymme för framtida generationer.

# --- 12e) plot ---
fig, axs = plt.subplots(1, 2, figsize=(13, 5))

# Vänster: utsläpp scenario 1 för att visa negativt
axs[0].plot(future_years, s1, color='steelblue')
axs[0].axhline(0, color='black', linewidth=0.8, linestyle='--')
axs[0].axvline(2070, color='gray', linewidth=0.6, linestyle='--', label='Nollutsläpp (2070)')
axs[0].fill_between(future_years, s1, 0,
                    where=np.array(s1) < 0,
                    color='steelblue', alpha=0.3, label='Negativa utsläpp')
axs[0].set_xlabel('År')
axs[0].set_ylabel('CO₂-utsläpp (GtC/år)')
axs[0].set_title('Scenario i: utsläppsutveckling')
axs[0].legend(fontsize=8)
axs[0].grid(True, alpha=0.4)

# Höger: temperaturrespons — peak och nedgång
axs[1].plot(years1, dt1pi, color='steelblue', label='Scenario i')
axs[1].axhline(1.5, color='black', linewidth=0.8, linestyle='--', label='1.5°C (Paris)')
axs[1].axhline(2.0, color='black', linewidth=0.8, linestyle=':',  label='2.0°C (Paris)')

# Markera temperaturtoppen
peak_idx = int(np.argmax(dt1pi))
peak_year = years1[peak_idx]
peak_temp = dt1pi[peak_idx]
axs[1].scatter(peak_year, peak_temp, color='steelblue', zorder=5, s=60)
axs[1].annotate(f'Topp: {peak_temp:.2f}°C ({peak_year})',
                xy=(peak_year, peak_temp),
                xytext=(10, -15),
                textcoords='offset points',
                fontsize=8)

axs[1].set_xlabel('År')
axs[1].set_ylabel('Temperaturökning (°C, relativt pre-industriellt)')
axs[1].set_title('Scenario i: temperaturpeak och nedgång')
axs[1].legend(fontsize=8)
axs[1].grid(True, alpha=0.4)

plt.suptitle('Task 12e: Negativa utsläpp och temperaturrespons')
plt.tight_layout()
plt.show()

# HUR KAN NEGATIVA UTSLÄPP REALISERAS:
# Det finns två huvudsakliga mekanismer. Den ena är naturbaserad — återbeskogning 
# och restaurering av ekosystem som myrar och mangrove som binder kol i biomassa och mark. 
# Den andra är teknisk — BECCS (bioenergy with carbon capture and storage) där 
# biomassa förbränns för energi men CO₂-utsläppen fångas och lagras geologiskt, 
# eller direkt luftinfångning (DAC) där maskiner extraherar CO₂ direkt ur atmosfären. 
# Gemensamt för alla är att de är antingen skalbarhets­begränsade (markbrist för återbeskogning) 
# eller extremt energi- och kostnadskrävande (DAC).

# VARFÖR LEDER NEGATIVA UTSLÄPP TILL PEAK-AND-DECLINE:
# När nettoutsläppen blir negativa minskar atmosfärens CO₂-koncentration. Lägre koncentration 
# ger lägre radiativ forcing, vilket innebär att systemet börjar stråla ut mer energi än det tar in
#  — temperaturen sjunker gradvis. Nedgången är trög eftersom djuphavet fortfarande har lagrad 
# värme som långsamt läcker tillbaka till ytan.
# Peak-and-decline-banor är centrala för 1.5°C-målet av en enkel anledning — med nuvarande utsläppstakt 
# kommer vi nästan säkert att överstiga 1.5°C tillfälligt. Negativa utsläpp gör det möjligt att överskrida 
# målet temporärt och sedan återvända under det, vilket kallas overshoot-and-return. 
# IPCC:s scenarier som begränsar uppvärmningen till 1.5°C förlitar sig nästan alla på just detta, eftersom en 
# rak linje under 1.5°C hela vägen kräver omedelliga och drastiska utsläppsminskningar som bedöms som politiskt 
# orealistiska. Risken är att man förlitar sig på framtida negativ-utsläppsteknologi som ännu inte finns i 
# tillräcklig skala, vilket skjuter bördan till framtida generationer.

# ==================================================================
# TASK 13: 
# - Antag utsläpp enligt scenario 3 som utgångspunkt
# - a) Utsläpp enligt 3 tills 2050 -> minskning av inkommande solstrålning (linjär?) med 4 w/M^2 till 2100 -> se vad som händer med
# global mean temperature fram till 2200
# ===================================================================


# Vi använder Scenario 3 (s3) som vi definierade i Task 12
# Vi använder lambda = 0.8 och motsvarande parametrar för enkelhetens skull
lam_13 = 0.8
k_13 = param_sets[0.8]['k']
s_13 = param_sets[0.8]['s']

# Kör baslinjesimulering för hela perioden (1765-2200) för Scenario 3
all_years, dT1_scenario3 = run_scenario(hist_years, hist_emissions, future_years, s3, lam=lam_13, k=k_13, s=s_13)
dT1_scenario3_pi = preindustrial_adj(all_years, dT1_scenario3)

# Skapa Geoengineering-forcing
rf_geo = np.zeros(len(all_years))
for i, y in enumerate(all_years):
    if 2050 <= y <= 2100:
        rf_geo[i] = -4.0  # W/m2 kylning

# Beräkna ny total forcing för Scenario 3 + Geoengineering
# Vi behöver hämta RF för CO2 och andra källor igen för att lägga till rf_geo
m_atm_13, _, _ = combined_ocean_biosphere(all_years, list(hist_emissions) + list(s3))
konc_13 = to_ppm(m_atm_13)
rf_co2_13 = np.array([rf(c) for c in konc_13])
rf_other_13 = get_rf_other(all_years) * s_13

rf_total_geo = rf_co2_13 + rf_other_13 + rf_geo

# Kör energibalansmodellen med den nya forcingen
dT1_geo, _ = energybalance(rf_total_geo, lam=lam_13, k=k_13)
dT1_geo = np.array(dT1_geo[1:])
dT1_geo_pi = preindustrial_adj(all_years, dT1_geo)

# ===================================================
# Plotta resultaten
# ===================================================

plt.figure(figsize=(10, 6))
plt.plot(all_years, dT1_scenario3_pi, color='firebrick', label='Scenario 3 (Utan Geoengineering)')
plt.plot(all_years, dT1_geo_pi, color='darkgreen', label='Scenario 3 + Geoengineering (2050-2100)')

# Formatering
plt.axvspan(2050, 2100, color='gray', alpha=0.2, label='Geoengineering aktiv')
plt.axhline(1.5, color='black', lw=0.8, ls='--')
plt.axhline(2.0, color='black', lw=0.8, ls=':')
plt.xlabel('År')
plt.ylabel('Temperaturökning (°C, rel. pre-industriellt)')
plt.title('Task 13a: Termination Shock vid avbrott av Geoengineering')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Temperatur precis vid start och slut av geoengineering
idx_2050 = all_years.index(2050)
idx_2100 = all_years.index(2100)
idx_2150 = all_years.index(2150)
idx_2200 = all_years.index(2200)

print(f"Temp år 2050 (geo startar): {dT1_geo_pi[idx_2050]:.2f}°C")
print(f"Temp år 2100 (geo slutar):  {dT1_geo_pi[idx_2100]:.2f}°C")
print(f"Temp år 2150:               {dT1_geo_pi[idx_2150]:.2f}°C")
print(f"Temp år 2200:               {dT1_geo_pi[idx_2200]:.2f}°C")

# Hur snabb är uppvärmningen efter avbrottet?
rate_geo = (dT1_geo_pi[idx_2100 + 11] - dT1_geo_pi[idx_2100 - 1]) / 12
rate_s3 = (dT1_geo_pi[idx_2100 - 88] - dT1_geo_pi[idx_2100 - 100]) / 12
print(f"Uppvärmingstakt (Derivata av årlig MGSTI) efter avbrott: {rate_geo:.2f}°C/år")
print(f"Uppvärmingstakt 2000-2012 före avbrott: {rate_s3:.2f}°C/år")
print(f'Takten efter avbrottet är alltså {(rate_geo/rate_s3):.2f} gånger större än takten före.')

# =======================================================
# 13c) Diskutera stuff

# Vad Geoengineering gör, och vad det inte gör: 
# Stratosfärisk aerosolinjektion minskar inkommande solstrålning och sänker temperaturen, men adresserar 
# inte den underliggande orsaken till klimatförändringen — den ökande CO2-koncentrationen i atmosfären. 
# CO2 fortsätter att ackumuleras, havsförsurningen fortsätter opåverkad, och så fort geoengineeringen avbryts — av politiska, 
# ekonomiska eller tekniska skäl — sker termination shock som simulerat i 13a). Modelldn visar att uppvärmningen efter
# avbrottet sker mycket snabbare  (ordningsmässigt ~10x) än den ursprungliga uppvärmningen, 
# vilket ger ekosystem och samhällen extremt lite tid att anpassa sig.

#Jämförelse med utsläppsreduktioner och negativ-utsläpp teknik:
# Utsläppsreduktion i energisystemet — förnybar energi, elektrifiering, 
# energieffektivisering — angriper problemet vid källan. 
# Det minskar CO₂-koncentrationen på lång sikt och är därmed förenligt med både temperaturmålen 
# och havsförsurningsproblematiken. Negativa utsläpp via BECCS eller återbeskogning kompletterar detta genom att aktivt 
# dra ner atmosfärisk CO₂, vilket möjliggör peak-and-decline-banor som visat i 12e).
# Geoengineering skiljer sig fundamentalt från båda dessa på ett viktigt sätt: det kräver permanent och kontinuerlig implementering. 
# Om utsläppen fortsätter enligt scenario 3 och geoengineeringen sedan avbryts är situationen värre än om den 
# aldrig påbörjades — man har skapat ett beroende utan att ha löst grundproblemet. 
# Det är en temporär symptombehandling som låser in framtida generationer i ett val mellan fortsatt geoengineering eller katastrofal snabbuppvärmning.

#Hållbarhetsprinciperna
# Ur ett hållbarhetsperspektiv kan man analysera geoengineering längs tre dimensioner:
# Intergenerationell rättvisa — en kärnprincip i hållbar utveckling är att inte kompromissa med framtida generationers möjligheter. 
# Geoengineering gör precis detta: det skjuter det egentliga problemet framåt och överlämnar ett ännu svårare dilemma 
# till kommande generationer som måste antingen fortsätta en teknologisk intervention de inte valt, 
# eller möta konsekvenserna av ett uppbyggt CO₂-överskott.
# Global rättvisa — effekterna av stratosfärisk aerosolinjektion är inte geografiskt jämnt fördelade. Förändringar i monsunmönster 
# och nederbördsfördelning drabbar regioner som inte nödvändigtvis har beslutat om eller gynnas av interventionen. 
# Det skapar ett demokratiskt legitimitetsproblem — vem har rätten att fatta beslut som påverkar 
# hela planetens klimatsystem?
# Systemisk hållbarhet — hållbar utveckling kräver att lösningar är robusta över tid och inte skapar nya sårbarhet. 
# Geoengineering skapar en extrem sårbarhet: ett enda politiskt beslut, en ekonomisk kris eller en konflikt kan avbryta 
# interventionen och utlösa termination shock. 
# Det är svårt att tänka sig en mindre robust lösning.

#Slutsats
# Geoengineering kan i teorin köpa tid — modell visar att −4 W/m² under 2050–2100 håller 
# temperaturen nere under den perioden — men det är inte en lösning, utan ett 
# riskabelt uppskjutande. Det är förenligt med kortsiktiga temperaturmål men 
# fundamentalt oförenligt med hållbar utvecklings principer om intergenerationell rättvisa, 
# global rättvisa och systemisk robusthet. Den enda väg som är långsiktigt förenlig med 
# Paris-avtalets mål och hållbarhetsprinciperna är snabb utsläppsreduktion 
# kombinerat med negativa utsläpp för att hantera det redan ackumulerade CO2-överskottet. 
# Geoengineering kan möjligen diskuteras som ett nödåtgärdsverktyg i extrema scenarion, men aldrig 
# som substitut för strukturell omställning av energisystemet.