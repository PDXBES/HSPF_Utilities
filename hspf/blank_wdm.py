from wdmtoolbox import wdmtoolbox


def create_blank_flow_dsn(wdm, dsn, tcode, tstep, description, location):
    tstype = 'FLOW'
    base_year = 1948
    # tcode -> 2 minute 3 hour
    # tstep = 1
    statid = str(dsn)
    scenario = "simulate"
    location = location
    description = description
    constituent = 'FLOW'
    tsfill = 0.0  # TODO need to provide feedback on fill
    wdmtoolbox.createnewdsn(wdm, dsn, tstype, base_year, tcode, tstep, statid, scenario, location, description, constituent,
                            tsfill)


output_blank_wdm = r"\\BESFile1\ASM_Projects\E11056_SW_Corridor_LR\models\Storm\Woods\Calibration_New\sim\HSPF\HRU_10.wdm"

# print("Create wdm")
wdmtoolbox.createnewwdm(output_blank_wdm, True)

tcode = 2
tstep = 5

#TODO should come from HSPF object
perlnds = [("Forest", "Flat", "Outwash", 1),
            ("Forest", "Mod", "Outwash", 2),
            ("Forest", "Stp", "Outwash", 3),
            ("Forest", "VStp", "Outwash", 33),
            ("Grass", "Flat", "Outwash", 7),
            ("Grass", "Mod", "Outwash", 8),
            ("Grass", "Stp", "Outwash", 9),
            ("Grass", "VStp", "Outwash", 39),
            ("Forest", "Flat", "Till", 10),
            ("Forest", "Mod", "Till", 11),
            ("Forest", "Stp", "Till", 12),
            ("Forest", "VStp", "Till", 42),
            ("Grass", "Flat", "Till", 16),
            ("Grass", "Mod", "Till", 17),
            ("Grass", "Stp", "Till", 18),
            ("Grass", "VStp", "Till", 48),
            ("Forest", "Flat", "Sat", 19),
            ("Forest", "Mod", "Sat", 20),
            ("Forest", "Stp", "Sat", 21),
            ("Forest", "VStp", "Sat", 51),
            ("Grass", "Flat", "Sat", 25),
            ("Grass", "Mod", "Sat", 26),
            ("Grass", "Stp", "Sat", 27),
            ("Grass", "VStp", "Sat", 57)
           ]

#TODO should come from HSPF object
implnds = [
    ("Bldg", "Stp", 1),
    ("Road", "Flat", 2),
    ("Road", "Mod", 3),
    ("Road", "Stp", 4),
    ("Road", "VStp", 5),
    ("Prkg", "Flat", 6),
    ("Prkg", "Mod", 7),
    ("Prkg", "Stp", 8),
    ("Prkg", "VStp", 9)
    ]

#TODO should use perlnd and implnd objects
# Perlnds
# write suro dsns
suro_base_dsn = 1000
for perlnd in perlnds:
    dsn = suro_base_dsn + perlnd[3]
    description = "SURO " + perlnd[0] + " " + perlnd[1] + " " + perlnd[2]
    location = str(dsn)
    create_blank_flow_dsn(output_blank_wdm, dsn, tcode, tstep, description, location)

# write ifwo dsns
ifwo_base_dsn = 1200
for perlnd in perlnds:
    dsn = ifwo_base_dsn + perlnd[3]
    description = "IFWO " + perlnd[0] + " " + perlnd[1] + " " + perlnd[2]
    location = str(dsn)
    create_blank_flow_dsn(output_blank_wdm, dsn, tcode, tstep, description, location)

# write agwo dsns
agwo_base_dsn = 1300
for perlnd in perlnds:
    dsn = agwo_base_dsn + perlnd[3]
    description = "AGWO " + perlnd[0] + " " + perlnd[1] + " " + perlnd[2]
    location = str(dsn)
    create_blank_flow_dsn(output_blank_wdm, dsn, tcode, tstep, description, location)

# Implnds
implnd_suro_base_dsn = 1100
# write suro dsns
for implnd in implnds:
    dsn = implnd_suro_base_dsn + implnd[2]
    description = "SURO " + implnd[0] + " " + implnd[1]
    location = str(dsn)
    create_blank_flow_dsn(output_blank_wdm, dsn, tcode, tstep, description, location)



