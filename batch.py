import run_hspf_swmm_excel as RunHspfSwmmExcel

excel_files = [

               # r"V:\HydroModHSPF\Models\Tryon\TryonMainStemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt4.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimplePredeveloped\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt4.xlsx",

               # r"V:\HydroModHSPF\Models\Tryon\TryonMainStemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt3.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainStemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt2.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainStemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt1.xlsx",
               #
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimplePredeveloped\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt3.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimplePredeveloped\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt1.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimplePredeveloped\HSPFSWMMInputAllSoils_Tryon_New_Calibration1_Pt2.xlsx"

               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_morevstp.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b3_3.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b323.xlsx",

               r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b342_lzns_inf_agwrc_lt_1.xlsx",
               r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b342_lzns_inf_agwrc_lt_4.xlsx",
               r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b342_lzns_inf_agwrc_lt_3.xlsx",
               r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b342_lzns_inf_agwrc_lt_2.xlsx",

               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b322.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b321.xlsx",
               #
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b313.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b312.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b311.xlsx",
               #
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b3_2.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b3_1.xlsx",
               #
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b32.xlsx",
               # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinalRGs\HSPFSWMMInputAllSoils_Tryon_Calibration_new_1 234_novstp_b31.xlsx",
               ]

# [r"V:\E11098_Council_Crest\model\CCCalibration\CCStorm_detailed_model_all_soils_existingIIEstimateV3\HSPFSWMMInputAllSoilsTryon161LEIA.xlsx",
#                r"V:\E11098_Council_Crest\model\CCCalibration\CCStorm_detailed_model_all_soils_existingIIEstimateV3\HSPFSWMMInputAllSoilsTryon.xlsx",
#                r"V:\E11098_Council_Crest\model\CCCalibration\CCStorm_detailed_model_all_soils_existingIIEstimateV3\HSPFSWMMInputAllSoilsTryon161.xlsx",
#
#                ]
    # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_Clark.xlsx",
    # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_SNOHO.xlsx",
    # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_Trust.xlsx",
    # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_WWHM.xlsx",
    # r"V:\HydroModHSPF\Models\Tryon\TryonMainstemSimpleIIFinal\HSPFSWMMInputAllSoils_Tryon_Fanno.xlsx"
            #]


for excel_file in excel_files:
    RunHspfSwmmExcel.main([excel_file])
