# Kursa_darbs_web_lietotne
Web-lietotne, kura prognozē basketbola spēles iznākumu divām(izvēlas lietotājs) koledžas komandām, balstoties uz konkrēta gada datiem. Prognozei ir izmantoti tādi komandu parametri ka ADJOE(regulētā uzbrukuma efektivitāte), ADJDE(regulētā aizsardzības efektivitāte), BARTHAG(spēka reitings),EFG_D(efektīvais metienu procents aizsardzībā),TORD(aizsardzības kļūdu rādītājs), 3P_O(trīspunktu metienu procents).  Prognozei var izvelēties jebkuru gadu, ja šajā gadā pastāv informācija par spēlēm. Ir izmantots Flask satvars.
Prognoze notiek sekojoši :
1) programma izmanto datu kopu, kura satur datus par komandām dažādos gados (https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset)
2) prognozēšanai ir izmantots RandomForestClassifier. Lai apmacītu klasifikatoru ir veidoti komandu pāri un par uzvārētāju skaitās tā komanda, kurai noteiktā periodā ir vairāk uzvaru. Tādējādi, klasifikators ir apmācīts, izmantojot abu komandu pazimju vektorus un "label" 1 vai 0, kas nozīmē "uzvārētāju" noteiktā laika periodā
3) Lietotne iz izvietota uz Azure virtuālas mašīnas(Linux)
4) Lietotāja prognozes saglabājas datubāzē u ntos var apskatīt atsevišķā lapā
