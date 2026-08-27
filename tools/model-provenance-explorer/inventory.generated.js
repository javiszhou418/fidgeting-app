window.MODEL_PROVENANCE = {
  "generatedAt": "2026-08-26T13:30:55.486Z",
  "repoRoot": "/Users/jiawei.zhou/Documents/Fidgeting app",
  "stageMeta": {
    "input": {
      "number": "01",
      "title": "你的 Input",
      "short": "输入",
      "description": "实拍、专利、正交图、视频帧与锁定规格"
    },
    "process": {
      "number": "02",
      "title": "中间 Process",
      "short": "过程",
      "description": "分析板、概念图、爆炸图、Blender/CLI 与验证"
    },
    "output": {
      "number": "03",
      "title": "Unity Output",
      "short": "输出",
      "description": "shipping 场景、材质、构图、批准或拒绝证据"
    }
  },
  "totals": {
    "image": 874,
    "model": 41,
    "document": 32,
    "other": 0,
    "unique": 947,
    "references": 10
  },
  "pipelines": [
    {
      "id": "magnetic-slide-tile",
      "name": "磁吸推牌",
      "productId": "magnetic-slide-tile",
      "status": "current",
      "statusLabel": "正式模型 · 建议重做外观",
      "summary": "输入最完整的一条链：实拍与专利结构 → 参数化六视图/爆炸概念 → Meshy 与 Unity 材质、布光、内部结构验证。",
      "diagnosis": "机构资料充足，但现模型的表面语言过于繁杂、磁体暴露感强，亮银高光也容易读成廉价镀铬。重做时应保留六档机构与真实行程，只重做外壳比例、分件、倒角与材质。",
      "rebuildFocus": [
        "先锁定原创轮廓和真实厚度",
        "保留六档磁吸与 13.6 mm 中心距",
        "减少装饰槽，明确金属/树脂分区",
        "从正交图建模，不从透视宣传图量尺寸"
      ],
      "stages": {
        "input": [
          {
            "label": "推牌实拍、产品与专利参考包",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling"
            ],
            "explicitFiles": [],
            "note": "22 张关键参考 + 1 张联系表；用于尺度、握持、层级和材质。",
            "state": "working",
            "files": [
              {
                "name": "00_contact_sheet.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/00_contact_sheet.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/00_contact_sheet.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/00_contact_sheet.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 310013
              },
              {
                "name": "01_kovo_transparent_internal_front.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 100062
              },
              {
                "name": "02_kovo_smoke_internal_track_closeup.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 74969
              },
              {
                "name": "03_kovo_thumb_grip.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 115415
              },
              {
                "name": "04_matrix_limite_slide_grip.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 67368
              },
              {
                "name": "05_matrix_limite_palm_scale.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 82630
              },
              {
                "name": "06_matrix_limite_dual_backplate.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 88343
              },
              {
                "name": "07_tita_pro_layered_body.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 94288
              },
              {
                "name": "08_usd1020916_perspective.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 291279
              },
              {
                "name": "09_usd1020916_front.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 210017
              },
              {
                "name": "10_usd1020916_rear.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 115467
              },
              {
                "name": "11_usd1020916_side.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 118475
              },
              {
                "name": "12_usd1020916_exploded_front.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 310989
              },
              {
                "name": "13_usd1020916_exploded_perspective.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224197
              },
              {
                "name": "14_cn218011061_internal_tracks_magnets.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 919237
              },
              {
                "name": "15_cn218011061_replaceable_panel.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 223426
              },
              {
                "name": "16_magnus_magnet_spacing_layout.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/16_magnus_magnet_spacing_layout.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/16_magnus_magnet_spacing_layout.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/16_magnus_magnet_spacing_layout.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 88505
              },
              {
                "name": "17_magnus_v8_material_palm_scale.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/17_magnus_v8_material_palm_scale.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/17_magnus_v8_material_palm_scale.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/17_magnus_v8_material_palm_scale.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 77084
              },
              {
                "name": "18_lautie_shuffle_v3_three_layer.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 188253
              },
              {
                "name": "19_lautie_shuffle_v3_action_sequence.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 120010
              },
              {
                "name": "20_lautie_shuffle_v3_layer_removal.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 110600
              },
              {
                "name": "21_lautie_shuffle_v3_magnet_detail.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 109287
              },
              {
                "name": "22_edcell_tapedrive_rotor_surface.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/22_edcell_tapedrive_rotor_surface.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/22_edcell_tapedrive_rotor_surface.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/22_edcell_tapedrive_rotor_surface.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 157131
              }
            ]
          },
          {
            "label": "专利拆解线框",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes"
            ],
            "explicitFiles": [],
            "note": "9 张结构裁图 + 联系表；只推断层级和爆炸方向。",
            "state": "working",
            "files": [
              {
                "name": "00_contact_sheet.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/00_contact_sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/00_contact_sheet.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/00_contact_sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 616480
              },
              {
                "name": "01_usd1020916_exploded_front_complete.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/01_usd1020916_exploded_front_complete.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/01_usd1020916_exploded_front_complete.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/01_usd1020916_exploded_front_complete.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 228732
              },
              {
                "name": "02_usd1020916_front_top_assembly.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/02_usd1020916_front_top_assembly.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/02_usd1020916_front_top_assembly.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/02_usd1020916_front_top_assembly.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 121696
              },
              {
                "name": "03_usd1020916_front_bottom_assembly.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/03_usd1020916_front_bottom_assembly.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/03_usd1020916_front_bottom_assembly.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/03_usd1020916_front_bottom_assembly.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 98170
              },
              {
                "name": "04_usd1020916_exploded_perspective_complete.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/04_usd1020916_exploded_perspective_complete.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/04_usd1020916_exploded_perspective_complete.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/04_usd1020916_exploded_perspective_complete.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 163963
              },
              {
                "name": "05_usd1020916_perspective_top_assembly.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/05_usd1020916_perspective_top_assembly.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/05_usd1020916_perspective_top_assembly.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/05_usd1020916_perspective_top_assembly.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 88192
              },
              {
                "name": "06_usd1020916_perspective_bottom_assembly.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/06_usd1020916_perspective_bottom_assembly.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/06_usd1020916_perspective_bottom_assembly.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/06_usd1020916_perspective_bottom_assembly.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 68534
              },
              {
                "name": "07_cn218011061_outer_shell.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/07_cn218011061_outer_shell.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/07_cn218011061_outer_shell.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/07_cn218011061_outer_shell.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 583818
              },
              {
                "name": "08_cn218011061_internal_tracks_and_magnets.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/08_cn218011061_internal_tracks_and_magnets.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/08_cn218011061_internal_tracks_and_magnets.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/08_cn218011061_internal_tracks_and_magnets.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 513036
              },
              {
                "name": "09_cn218011061_replaceable_panel.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/09_cn218011061_replaceable_panel.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/09_cn218011061_replaceable_panel.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes/09_cn218011061_replaceable_panel.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 220298
              }
            ]
          },
          {
            "label": "早期 EDC 多角度输入",
            "folders": [
              "Artifacts/EDC"
            ],
            "explicitFiles": [],
            "note": "侧、顶、端面等输入视图。",
            "state": "working",
            "files": [
              {
                "name": "Source_Edge_PosY.png",
                "path": "Artifacts/EDC/Source_Edge_PosY.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Edge_PosY.png",
                "url": "../../Artifacts/EDC/Source_Edge_PosY.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 138373
              },
              {
                "name": "Source_End_PosX.png",
                "path": "Artifacts/EDC/Source_End_PosX.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_End_PosX.png",
                "url": "../../Artifacts/EDC/Source_End_PosX.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 191987
              },
              {
                "name": "Source_Face_NegY.png",
                "path": "Artifacts/EDC/Source_Face_NegY.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Face_NegY.png",
                "url": "../../Artifacts/EDC/Source_Face_NegY.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 116230
              },
              {
                "name": "Source_Face_NegZ.png",
                "path": "Artifacts/EDC/Source_Face_NegZ.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Face_NegZ.png",
                "url": "../../Artifacts/EDC/Source_Face_NegZ.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 300737
              },
              {
                "name": "Source_Face_PosZ.png",
                "path": "Artifacts/EDC/Source_Face_PosZ.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Face_PosZ.png",
                "url": "../../Artifacts/EDC/Source_Face_PosZ.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 245714
              },
              {
                "name": "Source_Side.png",
                "path": "Artifacts/EDC/Source_Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Side.png",
                "url": "../../Artifacts/EDC/Source_Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 137083
              },
              {
                "name": "Source_Top.png",
                "path": "Artifacts/EDC/Source_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Source_Top.png",
                "url": "../../Artifacts/EDC/Source_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 353392
              }
            ]
          },
          {
            "label": "KOVO / Matrix / Clean EDC 分析板",
            "folders": [
              "assets/3d-analysis/2026-08-01"
            ],
            "explicitFiles": [],
            "note": "对推滑姿态、形体与材质的研究。",
            "state": "working",
            "files": [
              {
                "name": "02-kovo-slider-analysis.png",
                "path": "assets/3d-analysis/2026-08-01/02-kovo-slider-analysis.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/02-kovo-slider-analysis.png",
                "url": "../../assets/3d-analysis/2026-08-01/02-kovo-slider-analysis.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1968922
              },
              {
                "name": "03-matrix-edc-motion-analysis.png",
                "path": "assets/3d-analysis/2026-08-01/03-matrix-edc-motion-analysis.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/03-matrix-edc-motion-analysis.png",
                "url": "../../assets/3d-analysis/2026-08-01/03-matrix-edc-motion-analysis.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2030859
              },
              {
                "name": "04-clean-edc-form-analysis.png",
                "path": "assets/3d-analysis/2026-08-01/04-clean-edc-form-analysis.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/04-clean-edc-form-analysis.png",
                "url": "../../assets/3d-analysis/2026-08-01/04-clean-edc-form-analysis.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1968219
              }
            ]
          }
        ],
        "process": [
          {
            "label": "同源参数化六视图",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views"
            ],
            "explicitFiles": [],
            "note": "爆炸、顶、正、背、左、右由同一确定性几何生成。",
            "state": "working",
            "files": [
              {
                "name": "00_contact_sheet.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/00_contact_sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/00_contact_sheet.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/00_contact_sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 461873
              },
              {
                "name": "01_exploded.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/01_exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/01_exploded.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/01_exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2004834
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/02_top.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1048552
              },
              {
                "name": "03_front.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/03_front.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/03_front.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/03_front.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1436331
              },
              {
                "name": "04_back_underside.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/04_back_underside.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/04_back_underside.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/04_back_underside.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 946218
              },
              {
                "name": "05_left_end.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/05_left_end.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/05_left_end.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/05_left_end.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1715298
              },
              {
                "name": "06_right_end.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/06_right_end.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/06_right_end.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/06_right_end.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1708661
              },
              {
                "name": "contact.html",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/contact.html",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/contact.html",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/contact.html",
                "kind": "document",
                "extension": "HTML",
                "sizeBytes": 1568
              },
              {
                "name": "index.html",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/index.html",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/index.html",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/index.html",
                "kind": "document",
                "extension": "HTML",
                "sizeBytes": 5127
              },
              {
                "name": "model.js",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/model.js",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/model.js",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/model.js",
                "kind": "document",
                "extension": "JS",
                "sizeBytes": 19345
              },
              {
                "name": "README.md",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/README.md",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/README.md",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/README.md",
                "kind": "document",
                "extension": "MD",
                "sizeBytes": 3146
              },
              {
                "name": "render.cjs",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/render.cjs",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/render.cjs",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/render.cjs",
                "kind": "document",
                "extension": "CJS",
                "sizeBytes": 6750
              },
              {
                "name": "three.core.js",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.core.js",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.core.js",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.core.js",
                "kind": "document",
                "extension": "JS",
                "sizeBytes": 1401321
              },
              {
                "name": "three.module.js",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.module.js",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.module.js",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views/vendor/three.module.js",
                "kind": "document",
                "extension": "JS",
                "sizeBytes": 603380
              }
            ]
          },
          {
            "label": "旧 ImageGen 五视图",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts"
            ],
            "explicitFiles": [],
            "note": "左右视角和顶板不一致，已被参数化六视图取代。",
            "state": "superseded",
            "files": [
              {
                "name": "01_pushcard_3d_exploded_five_views_v1.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1994648
              },
              {
                "name": "01_pushcard_3d_exploded_five_views_v1.prompt.md",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.prompt.md",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.prompt.md",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.prompt.md",
                "kind": "document",
                "extension": "MD",
                "sizeBytes": 4039
              }
            ]
          },
          {
            "label": "磁吸 EDC 爆炸概念 V1–V4",
            "folders": [
              "Artifacts/EDC"
            ],
            "explicitFiles": [],
            "note": "从通用卡片结构逐步收敛到三层分件。",
            "state": "working",
            "files": [
              {
                "name": "CardMagneticFidget_Exploded_Concept_v1.png",
                "path": "Artifacts/EDC/CardMagneticFidget_Exploded_Concept_v1.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_Exploded_Concept_v1.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_Exploded_Concept_v1.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2380543
              },
              {
                "name": "CardMagneticFidget_FanExploded_Concept_v2.png",
                "path": "Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2258759
              },
              {
                "name": "CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "path": "Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2338648
              },
              {
                "name": "CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "path": "Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2521320
              }
            ]
          },
          {
            "label": "网格减面与法线验证",
            "folders": [
              "Artifacts/EDC/OptimizationValidation"
            ],
            "explicitFiles": [],
            "note": "不同三角面预算、Unity 金属材质和重算法线对照。",
            "state": "working",
            "files": [
              {
                "name": "Closeups_RecomputedNormals.png",
                "path": "Artifacts/EDC/OptimizationValidation/Closeups_RecomputedNormals.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/Closeups_RecomputedNormals.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/Closeups_RecomputedNormals.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1933803
              },
              {
                "name": "ContactSheet_AllTiers.png",
                "path": "Artifacts/EDC/OptimizationValidation/ContactSheet_AllTiers.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/ContactSheet_AllTiers.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/ContactSheet_AllTiers.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1666978
              },
              {
                "name": "ContactSheet_RecomputedNormals.png",
                "path": "Artifacts/EDC/OptimizationValidation/ContactSheet_RecomputedNormals.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/ContactSheet_RecomputedNormals.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/ContactSheet_RecomputedNormals.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1558656
              },
              {
                "name": "geometry-metrics.json",
                "path": "Artifacts/EDC/OptimizationValidation/geometry-metrics.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/geometry-metrics.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/geometry-metrics.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 3427
              },
              {
                "name": "500000-console.log",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-console.log",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-console.log",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-console.log",
                "kind": "document",
                "extension": "LOG",
                "sizeBytes": 501
              },
              {
                "name": "500000-launch.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-launch.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-launch.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-launch.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1087
              },
              {
                "name": "500000-summary.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-summary.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-summary.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/500000-summary.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 975
              },
              {
                "name": "750000-console.log",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-console.log",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-console.log",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-console.log",
                "kind": "document",
                "extension": "LOG",
                "sizeBytes": 855
              },
              {
                "name": "750000-launch.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-launch.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-launch.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-launch.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1087
              },
              {
                "name": "750000-summary.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-summary.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-summary.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/750000-summary.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 978
              },
              {
                "name": "device-app-before.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-before.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-before.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-before.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1362
              },
              {
                "name": "device-app-test-installed.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-test-installed.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-test-installed.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-app-test-installed.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1370
              },
              {
                "name": "device-details-preinstall.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-details-preinstall.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-details-preinstall.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-details-preinstall.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 875
              },
              {
                "name": "device-list-reconnect-retry.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect-retry.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect-retry.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect-retry.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 854
              },
              {
                "name": "device-list-reconnect.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/device-list-reconnect.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 848
              },
              {
                "name": "install-test-corrected.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-corrected.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-corrected.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-corrected.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1069
              },
              {
                "name": "install-test-root-session.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-root-session.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-root-session.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test-root-session.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1288
              },
              {
                "name": "install-test.log",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test.log",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test.log",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/install-test.log",
                "kind": "document",
                "extension": "LOG",
                "sizeBytes": 134
              },
              {
                "name": "restore-formal-app.json",
                "path": "Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/restore-formal-app.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/restore-formal-app.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/iPhoneAB-20260805-unlocked/restore-formal-app.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 1215
              },
              {
                "name": "metrics.csv",
                "path": "Artifacts/EDC/OptimizationValidation/metrics.csv",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/metrics.csv",
                "url": "../../Artifacts/EDC/OptimizationValidation/metrics.csv",
                "kind": "document",
                "extension": "CSV",
                "sizeBytes": 2162
              },
              {
                "name": "metrics.json",
                "path": "Artifacts/EDC/OptimizationValidation/metrics.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/metrics.json",
                "url": "../../Artifacts/EDC/OptimizationValidation/metrics.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 9499
              },
              {
                "name": "NormalsExperiment_1M.png",
                "path": "Artifacts/EDC/OptimizationValidation/NormalsExperiment_1M.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/NormalsExperiment_1M.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/NormalsExperiment_1M.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1268923
              },
              {
                "name": "QualityFirst_A0_vs_A1.png",
                "path": "Artifacts/EDC/OptimizationValidation/QualityFirst_A0_vs_A1.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/QualityFirst_A0_vs_A1.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/QualityFirst_A0_vs_A1.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1552397
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 536371
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 523745
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368902
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/baseline_1994857/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1030293
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516328
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 521158
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 381793
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/RecomputedNormalsExperiment/qem_a1_t1000000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1033026
              },
              {
                "name": "REPORT.md",
                "path": "Artifacts/EDC/OptimizationValidation/REPORT.md",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/REPORT.md",
                "url": "../../Artifacts/EDC/OptimizationValidation/REPORT.md",
                "kind": "document",
                "extension": "MD",
                "sizeBytes": 10000
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 536371
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 523745
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368903
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/baseline_1994857/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1030242
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 514928
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 520813
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368035
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t416273/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1011606
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515573
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 519998
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 376220
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t500000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1016927
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515380
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 520467
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 383426
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t750000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1032004
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516125
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 521356
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 382132
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_QualityFirstAgg0/qem_a1_t1000000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1032913
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 536371
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 523745
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368903
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/baseline_1994857/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1030242
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 510358
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515876
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 361048
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t180000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 992039
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 513535
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 520496
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 371708
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t250000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1002635
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 514361
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 521363
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 376858
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t350000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1014861
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515700
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 522228
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 383008
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t500000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1024467
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515160
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 520534
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 385110
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t750000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1031972
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516354
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 521148
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 381793
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals/qem_a1_t1000000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1033158
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 536371
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 523745
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368902
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/baseline_1994857/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1030289
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 534463
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 540713
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 374517
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t180000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1038364
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 535318
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 543818
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 391229
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t250000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1065904
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 534130
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 542106
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 394338
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t350000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1090172
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 535211
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 541289
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 400566
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t500000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1094874
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 531587
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 537747
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 399064
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t750000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1093537
              },
              {
                "name": "Hero.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Hero.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 531703
              },
              {
                "name": "Open.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Open.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 537365
              },
              {
                "name": "Side.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Side.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 390842
              },
              {
                "name": "Top.png",
                "path": "Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Top.png",
                "url": "../../Artifacts/EDC/OptimizationValidation/UnityMetal/qem_a1_t1000000/Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1089031
              }
            ]
          },
          {
            "label": "实际 3D 源与导出",
            "folders": [
              "unity/FidgetingApp/Assets/_EDC"
            ],
            "explicitFiles": [],
            "note": "Meshy 输入、清理网格与优化导出。",
            "state": "working",
            "files": [
              {
                "name": "L1_TopFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L1_TopFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L1_TopFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L1_TopFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 113368021
              },
              {
                "name": "L2_UpperShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L2_UpperShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L2_UpperShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L2_UpperShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 63520942
              },
              {
                "name": "L3_Gasket_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L3_Gasket_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L3_Gasket_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L3_Gasket_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 1145601
              },
              {
                "name": "L6_InnerFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L6_InnerFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L6_InnerFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L6_InnerFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 17767256
              },
              {
                "name": "L7_BottomShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L7_BottomShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L7_BottomShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Generated/Meshes/L7_BottomShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 67057290
              },
              {
                "name": "Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx",
                "path": "unity/FidgetingApp/Assets/_EDC/Source/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Source/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Source/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 71702092
              },
              {
                "name": "L1_TopFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L1_TopFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L1_TopFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L1_TopFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 30178849
              },
              {
                "name": "L2_UpperShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L2_UpperShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L2_UpperShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L2_UpperShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 17658592
              },
              {
                "name": "L3_Gasket_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L3_Gasket_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L3_Gasket_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L3_Gasket_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 354744
              },
              {
                "name": "L6_InnerFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L6_InnerFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L6_InnerFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L6_InnerFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 5038437
              },
              {
                "name": "L7_BottomShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L7_BottomShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L7_BottomShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t500000/L7_BottomShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 19041492
              },
              {
                "name": "L1_TopFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L1_TopFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L1_TopFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L1_TopFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 43323259
              },
              {
                "name": "L2_UpperShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L2_UpperShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L2_UpperShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L2_UpperShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 26188910
              },
              {
                "name": "L3_Gasket_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L3_Gasket_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L3_Gasket_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L3_Gasket_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 511089
              },
              {
                "name": "L6_InnerFrame_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L6_InnerFrame_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L6_InnerFrame_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L6_InnerFrame_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 7396850
              },
              {
                "name": "L7_BottomShell_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L7_BottomShell_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L7_BottomShell_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_EDC/Tests/OptimizationValidation/Generated/t750000/L7_BottomShell_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 27922900
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Unity 最终/设备构图帧",
            "folders": [
              "Artifacts/EDC"
            ],
            "explicitFiles": [],
            "note": "开合、侧面、顶面和 iPhone 纵向构图。",
            "state": "working",
            "files": [
              {
                "name": "Final_iPhone_Portrait.png",
                "path": "Artifacts/EDC/Final_iPhone_Portrait.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Final_iPhone_Portrait.png",
                "url": "../../Artifacts/EDC/Final_iPhone_Portrait.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 500251
              },
              {
                "name": "Final_Open.png",
                "path": "Artifacts/EDC/Final_Open.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Final_Open.png",
                "url": "../../Artifacts/EDC/Final_Open.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 421747
              },
              {
                "name": "Final_Side.png",
                "path": "Artifacts/EDC/Final_Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Final_Side.png",
                "url": "../../Artifacts/EDC/Final_Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368902
              },
              {
                "name": "Final_Top.png",
                "path": "Artifacts/EDC/Final_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/Final_Top.png",
                "url": "../../Artifacts/EDC/Final_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1030401
              }
            ]
          },
          {
            "label": "Unity 材质与布光迭代",
            "folders": [
              "Artifacts/EDC/DiffusedLighting_2026-08-09",
              "Artifacts/EDC/PolishedFineMetal_2026-08-09",
              "Artifacts/EDC/ResinMetalContrast_2026-08-09",
              "Artifacts/EDC/BroaderSofterHighlights_2026-08-09",
              "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09"
            ],
            "explicitFiles": [],
            "note": "Library、Hero、左右斜角、Top、Low 和内部打开视角。",
            "state": "working",
            "files": [
              {
                "name": "00_ContactSheet.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_ContactSheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_ContactSheet.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_ContactSheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1024744
              },
              {
                "name": "00_Previous_Current_Comparison.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_Previous_Current_Comparison.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_Previous_Current_Comparison.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_Previous_Current_Comparison.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2586628
              },
              {
                "name": "01_LibraryPreview.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/01_LibraryPreview.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4118927
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/02_AuthoredHero.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4037192
              },
              {
                "name": "03_LeftOblique.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/03_LeftOblique.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4152367
              },
              {
                "name": "04_RightOblique.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/04_RightOblique.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4128136
              },
              {
                "name": "05_Top.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/05_Top.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4144420
              },
              {
                "name": "06_LowAngle.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/06_LowAngle.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3894222
              },
              {
                "name": "07_OpenInteriorHero.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/07_OpenInteriorHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/07_OpenInteriorHero.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/07_OpenInteriorHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3977496
              },
              {
                "name": "08_OpenInteriorOblique.png",
                "path": "Artifacts/EDC/BroaderSofterHighlights_2026-08-09/08_OpenInteriorOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/BroaderSofterHighlights_2026-08-09/08_OpenInteriorOblique.png",
                "url": "../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/08_OpenInteriorOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4144271
              },
              {
                "name": "00_ContactSheet.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/00_ContactSheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/00_ContactSheet.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/00_ContactSheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1076657
              },
              {
                "name": "01_LibraryPreview.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/01_LibraryPreview.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4122712
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/02_AuthoredHero.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4043683
              },
              {
                "name": "03_LeftOblique.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/03_LeftOblique.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4146454
              },
              {
                "name": "04_RightOblique.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/04_RightOblique.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4139655
              },
              {
                "name": "05_Top.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/05_Top.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4162351
              },
              {
                "name": "06_LowAngle.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/06_LowAngle.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3898388
              },
              {
                "name": "07_OpenInteriorHero.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/07_OpenInteriorHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/07_OpenInteriorHero.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/07_OpenInteriorHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3989484
              },
              {
                "name": "08_OpenInteriorOblique.png",
                "path": "Artifacts/EDC/DiffusedLighting_2026-08-09/08_OpenInteriorOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/DiffusedLighting_2026-08-09/08_OpenInteriorOblique.png",
                "url": "../../Artifacts/EDC/DiffusedLighting_2026-08-09/08_OpenInteriorOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4154066
              },
              {
                "name": "00_ContactSheet.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/00_ContactSheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/00_ContactSheet.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/00_ContactSheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1479504
              },
              {
                "name": "01_LibraryPreview.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/01_LibraryPreview.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4072423
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/02_AuthoredHero.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4059906
              },
              {
                "name": "03_LeftOblique.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/03_LeftOblique.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4171953
              },
              {
                "name": "04_RightOblique.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/04_RightOblique.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4157404
              },
              {
                "name": "05_Top.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/05_Top.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4147113
              },
              {
                "name": "06_LowAngle.png",
                "path": "Artifacts/EDC/PolishedFineMetal_2026-08-09/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PolishedFineMetal_2026-08-09/06_LowAngle.png",
                "url": "../../Artifacts/EDC/PolishedFineMetal_2026-08-09/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3868815
              },
              {
                "name": "01_LibraryPreview.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/01_LibraryPreview.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 725609
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/02_AuthoredHero.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 621707
              },
              {
                "name": "03_LeftOblique.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/03_LeftOblique.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 692902
              },
              {
                "name": "04_RightOblique.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/04_RightOblique.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 713500
              },
              {
                "name": "05_Top.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/05_Top.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 788410
              },
              {
                "name": "06_LowAngle.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/06_LowAngle.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 386510
              },
              {
                "name": "ApprovalContactSheet.png",
                "path": "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/ApprovalContactSheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/ApprovalContactSheet.png",
                "url": "../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/ApprovalContactSheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477913
              },
              {
                "name": "00_ContactSheet.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/00_ContactSheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/00_ContactSheet.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/00_ContactSheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1078726
              },
              {
                "name": "01_LibraryPreview.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/01_LibraryPreview.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4123233
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/02_AuthoredHero.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4045748
              },
              {
                "name": "03_LeftOblique.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/03_LeftOblique.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4149713
              },
              {
                "name": "04_RightOblique.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/04_RightOblique.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4144887
              },
              {
                "name": "05_Top.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/05_Top.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4163633
              },
              {
                "name": "06_LowAngle.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/06_LowAngle.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3898805
              },
              {
                "name": "07_OpenInteriorHero.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/07_OpenInteriorHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/07_OpenInteriorHero.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/07_OpenInteriorHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3990855
              },
              {
                "name": "08_OpenInteriorOblique.png",
                "path": "Artifacts/EDC/ResinMetalContrast_2026-08-09/08_OpenInteriorOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/ResinMetalContrast_2026-08-09/08_OpenInteriorOblique.png",
                "url": "../../Artifacts/EDC/ResinMetalContrast_2026-08-09/08_OpenInteriorOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4154180
              }
            ]
          },
          {
            "label": "恢复与批准候选",
            "folders": [
              "Artifacts/RecoveryApprovalV22"
            ],
            "explicitFiles": [],
            "note": "真实 shipping 场景五角度与 Hero 联系表。",
            "state": "working",
            "files": [
              {
                "name": "magnetic-slide-tile-five-angle-contact.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-five-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-five-angle-contact.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-five-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1579800
              },
              {
                "name": "magnetic-slide-tile-hero.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-hero.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 569607
              },
              {
                "name": "magnetic-slide-tile-left.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-left.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 553772
              },
              {
                "name": "magnetic-slide-tile-low.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-low.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 574464
              },
              {
                "name": "magnetic-slide-tile-right.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-right.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 563043
              },
              {
                "name": "magnetic-slide-tile-top.png",
                "path": "Artifacts/RecoveryApprovalV22/magnetic-slide-tile-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/magnetic-slide-tile-top.png",
                "url": "../../Artifacts/RecoveryApprovalV22/magnetic-slide-tile-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 534587
              },
              {
                "name": "build22-model-5-magnetic-slide-tile.png",
                "path": "Artifacts/RecoveryApprovalV22/Native/build22-model-5-magnetic-slide-tile.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/Native/build22-model-5-magnetic-slide-tile.png",
                "url": "../../Artifacts/RecoveryApprovalV22/Native/build22-model-5-magnetic-slide-tile.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3595464
              }
            ]
          },
          {
            "label": "设计圣经批准证据",
            "folders": [
              "unity/FidgetingApp/Docs/DesignBibleAssets"
            ],
            "explicitFiles": [],
            "note": "当前只批准对应材质与柔光语言。",
            "state": "approved",
            "files": [
              {
                "name": "magnetic-slide-polished-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-polished-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-polished-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-polished-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1479504
              },
              {
                "name": "magnetic-slide-soft-highlight-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-soft-highlight-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-soft-highlight-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/magnetic-slide-soft-highlight-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1024744
              }
            ]
          },
          {
            "label": "Premium Display Case 中的全部推牌帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "展示盒、铭牌、灯光和比例的各轮 Unity 输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 288481
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 449003
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452234
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 336483
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 445303
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214242
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 317181
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 483436
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 481363
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368724
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477317
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 235295
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 276317
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 434828
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 422507
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 327214
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 420625
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 207528
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 311410
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476552
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476737
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 363812
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 472449
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232142
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 315351
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 480848
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 479544
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 367077
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 474951
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 234378
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 299412
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463682
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 465566
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 353789
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 464920
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 223590
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1696832
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1650971
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1498775
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1510592
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1563251
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1086895
              }
            ]
          }
        ]
      }
    },
    {
      "id": "magnetic-fan-card",
      "name": "磁吸扇牌",
      "productId": "magnetic-fan-card",
      "status": "current",
      "statusLabel": "正式模型 · 结构受 guardrail 锁定",
      "summary": "推牌/卡牌机构参考 → 扇牌爆炸概念 → Blender 背面实体轨道与磁体 → Unity 正背面、四档运动和牌面输出。",
      "diagnosis": "当前结构数据比外观可靠。重做不能破坏右下轴心、三片尺寸、轨道边界和磁体数量；优先重做牌面比例、边框、金属粗糙度与 artwork。",
      "rebuildFocus": [
        "保留 63.5 × 88.9 × 2.5 mm 单片尺寸",
        "保留右下轴心与 0/45/90° 展开",
        "后轨完整外轮廓距牌边 ≥ 6 mm",
        "正面去掉廉价镜面与多余轴圈"
      ],
      "stages": {
        "input": [
          {
            "label": "Lautie 三层卡牌与磁体参考",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling"
            ],
            "explicitFiles": [],
            "note": "三层机身、动作序列、层移除和磁体细节。",
            "state": "working",
            "files": [
              {
                "name": "18_lautie_shuffle_v3_three_layer.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/18_lautie_shuffle_v3_three_layer.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 188253
              },
              {
                "name": "19_lautie_shuffle_v3_action_sequence.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/19_lautie_shuffle_v3_action_sequence.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 120010
              },
              {
                "name": "20_lautie_shuffle_v3_layer_removal.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/20_lautie_shuffle_v3_layer_removal.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 110600
              },
              {
                "name": "21_lautie_shuffle_v3_magnet_detail.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/21_lautie_shuffle_v3_magnet_detail.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 109287
              }
            ]
          },
          {
            "label": "扇牌概念输入",
            "folders": [
              "Artifacts/EDC"
            ],
            "explicitFiles": [],
            "note": "卡片扇开和三层爆炸的早期视觉目标。",
            "state": "working",
            "files": [
              {
                "name": "CardMagneticFidget_FanExploded_Concept_v2.png",
                "path": "Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_FanExploded_Concept_v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2258759
              },
              {
                "name": "CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "path": "Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_FanExploded_ReferenceMatched_v3.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2338648
              },
              {
                "name": "CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "path": "Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "url": "../../Artifacts/EDC/CardMagneticFidget_ThreeLayerExploded_Corrected_v4.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2521320
              }
            ]
          },
          {
            "label": "冻结建模合同",
            "folders": [],
            "explicitFiles": [
              "unity/FidgetingApp/Docs/FanCardModelingGuardrails.md",
              "unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json"
            ],
            "note": "重做必须从这些尺寸和坐标出发。",
            "state": "locked",
            "files": [
              {
                "name": "fan_card_guardrails.json",
                "path": "unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json",
                "url": "../../unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json",
                "kind": "document",
                "extension": "JSON",
                "sizeBytes": 2158
              },
              {
                "name": "FanCardModelingGuardrails.md",
                "path": "unity/FidgetingApp/Docs/FanCardModelingGuardrails.md",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/FanCardModelingGuardrails.md",
                "url": "../../unity/FidgetingApp/Docs/FanCardModelingGuardrails.md",
                "kind": "document",
                "extension": "MD",
                "sizeBytes": 6335
              }
            ]
          }
        ],
        "process": [
          {
            "label": "Blender 背面机构预览",
            "folders": [
              "Artifacts/FanCardBlenderPreview"
            ],
            "explicitFiles": [],
            "note": "实体网孔、弧形暗槽和磁体可见性。",
            "state": "working",
            "files": [
              {
                "name": "fan-card-back-grille-close.png",
                "path": "Artifacts/FanCardBlenderPreview/fan-card-back-grille-close.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardBlenderPreview/fan-card-back-grille-close.png",
                "url": "../../Artifacts/FanCardBlenderPreview/fan-card-back-grille-close.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1644919
              },
              {
                "name": "fan-card-back-grille-hero.png",
                "path": "Artifacts/FanCardBlenderPreview/fan-card-back-grille-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardBlenderPreview/fan-card-back-grille-hero.png",
                "url": "../../Artifacts/FanCardBlenderPreview/fan-card-back-grille-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1369593
              },
              {
                "name": "fan-card-back-grille-orthographic.png",
                "path": "Artifacts/FanCardBlenderPreview/fan-card-back-grille-orthographic.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardBlenderPreview/fan-card-back-grille-orthographic.png",
                "url": "../../Artifacts/FanCardBlenderPreview/fan-card-back-grille-orthographic.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1282352
              }
            ]
          },
          {
            "label": "几何门禁对照",
            "folders": [
              "Artifacts/FanCardGeometryValidation"
            ],
            "explicitFiles": [],
            "note": "低角、侧面和六视图的几何回归证据。",
            "state": "working",
            "files": [
              {
                "name": "after-loop1-low.png",
                "path": "Artifacts/FanCardGeometryValidation/after-loop1-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardGeometryValidation/after-loop1-low.png",
                "url": "../../Artifacts/FanCardGeometryValidation/after-loop1-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1182737
              },
              {
                "name": "after-loop1-side-profile.png",
                "path": "Artifacts/FanCardGeometryValidation/after-loop1-side-profile.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardGeometryValidation/after-loop1-side-profile.png",
                "url": "../../Artifacts/FanCardGeometryValidation/after-loop1-side-profile.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 988494
              },
              {
                "name": "after-loop1-six-view.png",
                "path": "Artifacts/FanCardGeometryValidation/after-loop1-six-view.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardGeometryValidation/after-loop1-six-view.png",
                "url": "../../Artifacts/FanCardGeometryValidation/after-loop1-six-view.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1037495
              },
              {
                "name": "before-build25-low.png",
                "path": "Artifacts/FanCardGeometryValidation/before-build25-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardGeometryValidation/before-build25-low.png",
                "url": "../../Artifacts/FanCardGeometryValidation/before-build25-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1761423
              }
            ]
          },
          {
            "label": "Blender 源与发布网格",
            "folders": [],
            "explicitFiles": [
              "unity/FidgetingApp/ArtSource/FanCard/FanCardBackMechanism.blend",
              "unity/FidgetingApp/Assets/_FanCard/Models/FanCardBackMechanism.fbx"
            ],
            "note": "当前可复现源和 Unity 发布网格。",
            "state": "locked",
            "files": [
              {
                "name": "FanCardBackMechanism.blend",
                "path": "unity/FidgetingApp/ArtSource/FanCard/FanCardBackMechanism.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/FanCard/FanCardBackMechanism.blend",
                "url": "../../unity/FidgetingApp/ArtSource/FanCard/FanCardBackMechanism.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 274341
              },
              {
                "name": "FanCardBackMechanism.fbx",
                "path": "unity/FidgetingApp/Assets/_FanCard/Models/FanCardBackMechanism.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_FanCard/Models/FanCardBackMechanism.fbx",
                "url": "../../unity/FidgetingApp/Assets/_FanCard/Models/FanCardBackMechanism.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 359452
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Unity shipping 多角度/运动/特写",
            "folders": [
              "Artifacts/FanCardMaterialPreview"
            ],
            "explicitFiles": [],
            "note": "Top、Hero、左右斜角、Low、Back、Side、0/30/60/90° 与结构特写。",
            "state": "working",
            "files": [
              {
                "name": "fan-card-aaa-hero.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-aaa-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-aaa-hero.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-aaa-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2171322
              },
              {
                "name": "fan-card-aaa-top.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-aaa-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-aaa-top.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-aaa-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2077826
              },
              {
                "name": "fan-card-ace-closeup.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-ace-closeup.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-ace-closeup.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-ace-closeup.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 702030
              },
              {
                "name": "fan-card-adaptive-contact-sheet.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-adaptive-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-adaptive-contact-sheet.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-adaptive-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 984999
              },
              {
                "name": "fan-card-axis-closeup.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-axis-closeup.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-axis-closeup.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-axis-closeup.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 922060
              },
              {
                "name": "fan-card-back-track-closeup.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-back-track-closeup.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-back-track-closeup.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-back-track-closeup.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1026290
              },
              {
                "name": "fan-card-back.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-back.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-back.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-back.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2024258
              },
              {
                "name": "fan-card-bearing-closeup.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-bearing-closeup.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-bearing-closeup.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-bearing-closeup.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 856171
              },
              {
                "name": "fan-card-center-hole-spacing-approval.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-center-hole-spacing-approval.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-center-hole-spacing-approval.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-center-hole-spacing-approval.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1245440
              },
              {
                "name": "fan-card-corner-index-bottom-right-closeup.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-corner-index-bottom-right-closeup.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-corner-index-bottom-right-closeup.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-corner-index-bottom-right-closeup.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 670828
              },
              {
                "name": "fan-card-default-two-step-45deg-approval.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-default-two-step-45deg-approval.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-default-two-step-45deg-approval.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-default-two-step-45deg-approval.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1632865
              },
              {
                "name": "fan-card-front-closed.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-front-closed.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-front-closed.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-front-closed.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1856265
              },
              {
                "name": "fan-card-hero.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-hero.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2171131
              },
              {
                "name": "fan-card-left.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-left.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2201173
              },
              {
                "name": "fan-card-library-centered.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-library-centered.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-library-centered.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-library-centered.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2207319
              },
              {
                "name": "fan-card-low.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-low.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1672567
              },
              {
                "name": "fan-card-motion-00.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-motion-00.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-motion-00.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-motion-00.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2170735
              },
              {
                "name": "fan-card-motion-30.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-motion-30.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-motion-30.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-motion-30.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2193579
              },
              {
                "name": "fan-card-motion-60.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-motion-60.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-motion-60.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-motion-60.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2188516
              },
              {
                "name": "fan-card-motion-90-to-00-contact-sheet.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-motion-90-to-00-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-motion-90-to-00-contact-sheet.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-motion-90-to-00-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 305950
              },
              {
                "name": "fan-card-motion-90.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-motion-90.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-motion-90.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-motion-90.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2164906
              },
              {
                "name": "fan-card-qka-hero.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-qka-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-qka-hero.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-qka-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2171121
              },
              {
                "name": "fan-card-qka-top.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-qka-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-qka-top.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-qka-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2078242
              },
              {
                "name": "fan-card-right.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-right.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2217027
              },
              {
                "name": "fan-card-side-profile.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-side-profile.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-side-profile.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-side-profile.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1394061
              },
              {
                "name": "fan-card-stable-interaction-contact-sheet.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-stable-interaction-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-stable-interaction-contact-sheet.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-stable-interaction-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 384372
              },
              {
                "name": "fan-card-top.png",
                "path": "Artifacts/FanCardMaterialPreview/fan-card-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardMaterialPreview/fan-card-top.png",
                "url": "../../Artifacts/FanCardMaterialPreview/fan-card-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2078242
              }
            ]
          },
          {
            "label": "原生目录页预览",
            "folders": [
              "Artifacts/FanCardNativeCatalogPreview"
            ],
            "explicitFiles": [],
            "note": "第六页原生目录中的真实模型。",
            "state": "working",
            "files": [
              {
                "name": "fan-card-sixth-page.png",
                "path": "Artifacts/FanCardNativeCatalogPreview/fan-card-sixth-page.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/FanCardNativeCatalogPreview/fan-card-sixth-page.png",
                "url": "../../Artifacts/FanCardNativeCatalogPreview/fan-card-sixth-page.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2730937
              }
            ]
          },
          {
            "label": "设计圣经批准联系表",
            "folders": [],
            "explicitFiles": [
              "unity/FidgetingApp/Docs/DesignBibleAssets/fan-card-approved-contact-sheet.png"
            ],
            "note": "当前批准的呈现证据。",
            "state": "approved",
            "files": [
              {
                "name": "fan-card-approved-contact-sheet.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/fan-card-approved-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/fan-card-approved-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/fan-card-approved-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 984999
              }
            ]
          },
          {
            "label": "Premium Display Case 中的全部扇牌帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "展示盒内六角度及多轮铭牌/灯光输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 304274
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 489011
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 447433
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 369507
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476168
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224681
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 358793
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 540853
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 490199
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 415873
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 518743
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 258618
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 292614
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 486595
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 428635
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 363803
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455931
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 219832
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 334942
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 519772
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477169
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 401168
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 508637
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 245049
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 340339
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 526387
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 481165
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 405389
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 511654
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 248857
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 316647
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 501478
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460646
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 384323
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 493112
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232722
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1684331
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1684598
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1481520
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1520268
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1580862
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1077251
              }
            ]
          }
        ]
      }
    },
    {
      "id": "metal-three-blade",
      "name": "三叶金属",
      "productId": "metal-three-blade",
      "status": "current",
      "statusLabel": "正式模型 · 建议重做造型",
      "summary": "正交/爆炸参考与材质分析 → Blender 三叶模型及轴心修复 → Unity 柔光、皮肤、贴纸与展示盒多角度。",
      "diagnosis": "当前版本经历过多次轴心、轴圈、材质和贴纸修补，说明基础轮廓与中心结构没有一次解决。重做时应先冻结 silhouette、厚度和真实机械轴，再做皮肤。",
      "rebuildFocus": [
        "先重做三叶过渡与中心轴承层级",
        "所有动态件围绕唯一机械原点",
        "取消悬浮轴圈与装饰配重",
        "皮肤只改变表面，不改变几何"
      ],
      "stages": {
        "input": [
          {
            "label": "三叶 Rotor 五视图与爆炸参考",
            "folders": [
              "unity/FidgetingApp/Docs/ModelingReferences"
            ],
            "explicitFiles": [],
            "note": "四套正交/爆炸目标图。",
            "state": "working",
            "files": [
              {
                "name": "fidget_rotor_exploded_reference_v1.png",
                "path": "unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_exploded_reference_v1.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_exploded_reference_v1.png",
                "url": "../../unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_exploded_reference_v1.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1805553
              },
              {
                "name": "fidget_rotor_orthographic_5view_v1.png",
                "path": "unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v1.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v1.png",
                "url": "../../unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v1.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1206801
              },
              {
                "name": "fidget_rotor_orthographic_5view_v2_curved.png",
                "path": "unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v2_curved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v2_curved.png",
                "url": "../../unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v2_curved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1464080
              },
              {
                "name": "fidget_rotor_orthographic_5view_v3_large_center_chamfered.png",
                "path": "unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v3_large_center_chamfered.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v3_large_center_chamfered.png",
                "url": "../../unity/FidgetingApp/Docs/ModelingReferences/fidget_rotor_orthographic_5view_v3_large_center_chamfered.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1540907
              }
            ]
          },
          {
            "label": "三叶形体、爆炸与材质分析板",
            "folders": [
              "assets/3d-analysis/2026-08-01"
            ],
            "explicitFiles": [],
            "note": "形体、镜头、PBR 分区和棚拍灯光。",
            "state": "working",
            "files": [
              {
                "name": "01-three-blade-spinner-analysis.png",
                "path": "assets/3d-analysis/2026-08-01/01-three-blade-spinner-analysis.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/01-three-blade-spinner-analysis.png",
                "url": "../../assets/3d-analysis/2026-08-01/01-three-blade-spinner-analysis.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1894722
              },
              {
                "name": "05-three-blade-storyboard-reference-style.png",
                "path": "assets/3d-analysis/2026-08-01/05-three-blade-storyboard-reference-style.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/05-three-blade-storyboard-reference-style.png",
                "url": "../../assets/3d-analysis/2026-08-01/05-three-blade-storyboard-reference-style.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1794957
              },
              {
                "name": "06-three-blade-orthographic-exploded-reference-style.png",
                "path": "assets/3d-analysis/2026-08-01/06-three-blade-orthographic-exploded-reference-style.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/06-three-blade-orthographic-exploded-reference-style.png",
                "url": "../../assets/3d-analysis/2026-08-01/06-three-blade-orthographic-exploded-reference-style.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1754579
              },
              {
                "name": "07-three-blade-series-01-storyboard.png",
                "path": "assets/3d-analysis/2026-08-01/07-three-blade-series-01-storyboard.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/07-three-blade-series-01-storyboard.png",
                "url": "../../assets/3d-analysis/2026-08-01/07-three-blade-series-01-storyboard.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1875896
              },
              {
                "name": "08-three-blade-series-02-orthographic-exploded.png",
                "path": "assets/3d-analysis/2026-08-01/08-three-blade-series-02-orthographic-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/08-three-blade-series-02-orthographic-exploded.png",
                "url": "../../assets/3d-analysis/2026-08-01/08-three-blade-series-02-orthographic-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1818466
              },
              {
                "name": "09-three-blade-series-03-material-lighting.png",
                "path": "assets/3d-analysis/2026-08-01/09-three-blade-series-03-material-lighting.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/09-three-blade-series-03-material-lighting.png",
                "url": "../../assets/3d-analysis/2026-08-01/09-three-blade-series-03-material-lighting.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1510091
              },
              {
                "name": "10-three-blade-series-03-material-lighting-reference-layout.png",
                "path": "assets/3d-analysis/2026-08-01/10-three-blade-series-03-material-lighting-reference-layout.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/assets/3d-analysis/2026-08-01/10-three-blade-series-03-material-lighting-reference-layout.png",
                "url": "../../assets/3d-analysis/2026-08-01/10-three-blade-series-03-material-lighting-reference-layout.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1390882
              }
            ]
          }
        ],
        "process": [
          {
            "label": "早期 Blender 多角度与爆炸图",
            "folders": [
              "Artifacts"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、Side、左右斜角和爆炸。",
            "state": "working",
            "files": [
              {
                "name": "three-blade-edc-exploded.png",
                "path": "Artifacts/three-blade-edc-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-exploded.png",
                "url": "../../Artifacts/three-blade-edc-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 227969
              },
              {
                "name": "three-blade-edc-left-oblique.png",
                "path": "Artifacts/three-blade-edc-left-oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-left-oblique.png",
                "url": "../../Artifacts/three-blade-edc-left-oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 266588
              },
              {
                "name": "three-blade-edc-preview.png",
                "path": "Artifacts/three-blade-edc-preview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-preview.png",
                "url": "../../Artifacts/three-blade-edc-preview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 298397
              },
              {
                "name": "three-blade-edc-right-oblique.png",
                "path": "Artifacts/three-blade-edc-right-oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-right-oblique.png",
                "url": "../../Artifacts/three-blade-edc-right-oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 254188
              },
              {
                "name": "three-blade-edc-side.png",
                "path": "Artifacts/three-blade-edc-side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-side.png",
                "url": "../../Artifacts/three-blade-edc-side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 160510
              },
              {
                "name": "three-blade-edc-top.png",
                "path": "Artifacts/three-blade-edc-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/three-blade-edc-top.png",
                "url": "../../Artifacts/three-blade-edc-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 374577
              }
            ]
          },
          {
            "label": "Blender 结构预览",
            "folders": [
              "unity/FidgetingApp/Artifacts/BlenderThreeBlade"
            ],
            "explicitFiles": [],
            "note": "Blender 生成结果与结构检查。",
            "state": "working",
            "files": [
              {
                "name": "three-blade-spinner-hero.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 994443
              },
              {
                "name": "three-blade-spinner-top.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-top.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderThreeBlade/three-blade-spinner-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 855028
              }
            ]
          },
          {
            "label": "转子轴心修复两轮",
            "folders": [
              "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix",
              "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2"
            ],
            "explicitFiles": [],
            "note": "修复转子、轴承外圈和固定指盖同轴。",
            "state": "working",
            "files": [
              {
                "name": "axis-spin-contact-v2.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/axis-spin-contact-v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/axis-spin-contact-v2.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/axis-spin-contact-v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 49551
              },
              {
                "name": "multi-angle-contact-v2.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/multi-angle-contact-v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/multi-angle-contact-v2.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/multi-angle-contact-v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 58859
              },
              {
                "name": "spin-000-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-000-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-000-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-000-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 95824
              },
              {
                "name": "spin-030-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-030-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-030-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-030-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 97407
              },
              {
                "name": "spin-060-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-060-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-060-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-060-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 97117
              },
              {
                "name": "spin-090-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-090-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-090-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-090-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 97207
              },
              {
                "name": "spin-120-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-120-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-120-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/spin-120-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 95887
              },
              {
                "name": "view-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 95997
              },
              {
                "name": "view-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 71225
              },
              {
                "name": "view-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 62076
              },
              {
                "name": "view-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 81333
              },
              {
                "name": "view-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2/view-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 170367
              },
              {
                "name": "approval-multi-angle-contact.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/approval-multi-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/approval-multi-angle-contact.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/approval-multi-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 96600
              },
              {
                "name": "axis-spin-contact.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/axis-spin-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/axis-spin-contact.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/axis-spin-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 79959
              },
              {
                "name": "spin-000-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-000-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-000-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-000-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 78253
              },
              {
                "name": "spin-030-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-030-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-030-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-030-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 76889
              },
              {
                "name": "spin-060-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-060-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-060-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-060-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 78795
              },
              {
                "name": "spin-090-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-090-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-090-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-090-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 80499
              },
              {
                "name": "spin-120-axis-overlay.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-120-axis-overlay.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-120-axis-overlay.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/spin-120-axis-overlay.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 78557
              },
              {
                "name": "view-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 78402
              },
              {
                "name": "view-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 63662
              },
              {
                "name": "view-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 53748
              },
              {
                "name": "view-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 64282
              },
              {
                "name": "view-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix/view-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 120030
              }
            ]
          },
          {
            "label": "十档金属皮肤",
            "folders": [
              "Artifacts/ThreeBladeMetalSkins"
            ],
            "explicitFiles": [],
            "note": "雾银、枪灰、夜航、钨金、冰银、蓝钢、赤铜、钛虹、黑曜、镜铬。",
            "state": "working",
            "files": [
              {
                "name": "lv001-factory-silver.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv001-factory-silver.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv001-factory-silver.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv001-factory-silver.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217998
              },
              {
                "name": "lv005-gunmetal-brush.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv005-gunmetal-brush.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv005-gunmetal-brush.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv005-gunmetal-brush.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 215541
              },
              {
                "name": "lv010-night-cyan-index.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv010-night-cyan-index.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv010-night-cyan-index.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv010-night-cyan-index.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 189375
              },
              {
                "name": "lv020-tungsten-honeycomb.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv020-tungsten-honeycomb.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv020-tungsten-honeycomb.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv020-tungsten-honeycomb.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 212309
              },
              {
                "name": "lv035-ice-guilloche.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv035-ice-guilloche.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv035-ice-guilloche.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv035-ice-guilloche.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217001
              },
              {
                "name": "lv050-blue-damascus.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv050-blue-damascus.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv050-blue-damascus.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv050-blue-damascus.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 221422
              },
              {
                "name": "lv065-copper-circuit.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv065-copper-circuit.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv065-copper-circuit.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv065-copper-circuit.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 207075
              },
              {
                "name": "lv075-titanium-heat.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv075-titanium-heat.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv075-titanium-heat.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv075-titanium-heat.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 201520
              },
              {
                "name": "lv090-meteor-obsidian.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv090-meteor-obsidian.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv090-meteor-obsidian.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv090-meteor-obsidian.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 195952
              },
              {
                "name": "lv100-mirror-aurora.png",
                "path": "Artifacts/ThreeBladeMetalSkins/lv100-mirror-aurora.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ThreeBladeMetalSkins/lv100-mirror-aurora.png",
                "url": "../../Artifacts/ThreeBladeMetalSkins/lv100-mirror-aurora.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 198521
              }
            ]
          },
          {
            "label": "三叶 Blender/Unity 模型文件",
            "folders": [
              "unity/FidgetingApp/ArtSource/ThreeBladeSpinner",
              "unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade"
            ],
            "explicitFiles": [],
            "note": "可编辑源和 Unity 导出。",
            "state": "working",
            "files": [
              {
                "name": "ThreeBladeSpinner.blend",
                "path": "unity/FidgetingApp/ArtSource/ThreeBladeSpinner/ThreeBladeSpinner.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/ThreeBladeSpinner/ThreeBladeSpinner.blend",
                "url": "../../unity/FidgetingApp/ArtSource/ThreeBladeSpinner/ThreeBladeSpinner.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 213778
              },
              {
                "name": "ThreeBladeSpinner_Collision.fbx",
                "path": "unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner_Collision.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner_Collision.fbx",
                "url": "../../unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner_Collision.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 51468
              },
              {
                "name": "ThreeBladeSpinner.fbx",
                "path": "unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.fbx",
                "url": "../../unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 667260
              },
              {
                "name": "ThreeBladeSpinner.glb",
                "path": "unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.glb",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.glb",
                "url": "../../unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.glb",
                "kind": "model",
                "extension": "GLB",
                "sizeBytes": 882204
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Unity 柔光 shipping 预览",
            "folders": [
              "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview"
            ],
            "explicitFiles": [],
            "note": "模型在正式场景中的多角度和联系表。",
            "state": "working",
            "files": [
              {
                "name": "gold-four-wing-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2095757
              },
              {
                "name": "gold-four-wing-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/gold-four-wing-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2098068
              },
              {
                "name": "graphite-two-lobe-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2064029
              },
              {
                "name": "graphite-two-lobe-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/graphite-two-lobe-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2056718
              },
              {
                "name": "magnetic-fan-card-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1920202
              },
              {
                "name": "magnetic-fan-card-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-fan-card-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1928771
              },
              {
                "name": "magnetic-slide-tile-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2021076
              },
              {
                "name": "magnetic-slide-tile-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/magnetic-slide-tile-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2048070
              },
              {
                "name": "metal-three-blade-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2096548
              },
              {
                "name": "metal-three-blade-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/metal-three-blade-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2098130
              },
              {
                "name": "pointed-three-blade-parallax-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-parallax-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2095864
              },
              {
                "name": "pointed-three-blade-unity.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-unity.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/pointed-three-blade-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2098357
              },
              {
                "name": "spinner-soft-lighting-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/spinner-soft-lighting-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/spinner-soft-lighting-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview/spinner-soft-lighting-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1184513
              }
            ]
          },
          {
            "label": "轴圈移除后的 Unity 预览",
            "folders": [
              "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、左右斜角、Low、Phone。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 75253
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 127781
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 56504
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 62384
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 49396
              },
              {
                "name": "contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade/contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 55976
              }
            ]
          },
          {
            "label": "恢复批准候选",
            "folders": [
              "Artifacts/RecoveryApprovalV22"
            ],
            "explicitFiles": [],
            "note": "五角度与 Hero。",
            "state": "working",
            "files": [
              {
                "name": "metal-three-blade-five-angle-contact.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-five-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-five-angle-contact.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-five-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1116517
              },
              {
                "name": "metal-three-blade-hero.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-hero.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 525330
              },
              {
                "name": "metal-three-blade-left.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-left.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 512450
              },
              {
                "name": "metal-three-blade-low.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-low.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 508759
              },
              {
                "name": "metal-three-blade-right.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-right.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516247
              },
              {
                "name": "metal-three-blade-top.png",
                "path": "Artifacts/RecoveryApprovalV22/metal-three-blade-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/metal-three-blade-top.png",
                "url": "../../Artifacts/RecoveryApprovalV22/metal-three-blade-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 490758
              }
            ]
          },
          {
            "label": "贴纸角度验证 V20/V21",
            "folders": [
              "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20",
              "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21"
            ],
            "explicitFiles": [],
            "note": "图形、文字、细线贴纸在多角度下的共形表现。",
            "state": "working",
            "files": [
              {
                "name": "01-01-pictogram-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-01-pictogram-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-01-pictogram-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-01-pictogram-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 228684
              },
              {
                "name": "01-02-pictogram-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-02-pictogram-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-02-pictogram-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-02-pictogram-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 180879
              },
              {
                "name": "01-03-pictogram-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-03-pictogram-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-03-pictogram-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-03-pictogram-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 154501
              },
              {
                "name": "01-04-pictogram-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-04-pictogram-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-04-pictogram-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-04-pictogram-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 141132
              },
              {
                "name": "01-05-pictogram-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-05-pictogram-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-05-pictogram-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/01-05-pictogram-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 97155
              },
              {
                "name": "02-01-text-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-01-text-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-01-text-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-01-text-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 220178
              },
              {
                "name": "02-02-text-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-02-text-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-02-text-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-02-text-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 172709
              },
              {
                "name": "02-03-text-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-03-text-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-03-text-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-03-text-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 150350
              },
              {
                "name": "02-04-text-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-04-text-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-04-text-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-04-text-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 136897
              },
              {
                "name": "02-05-text-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-05-text-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-05-text-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/02-05-text-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 94662
              },
              {
                "name": "03-01-thin-line-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-01-thin-line-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-01-thin-line-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-01-thin-line-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 212283
              },
              {
                "name": "03-02-thin-line-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-02-thin-line-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-02-thin-line-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-02-thin-line-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 171501
              },
              {
                "name": "03-03-thin-line-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-03-thin-line-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-03-thin-line-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-03-thin-line-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 147676
              },
              {
                "name": "03-04-thin-line-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-04-thin-line-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-04-thin-line-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-04-thin-line-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 133783
              },
              {
                "name": "03-05-thin-line-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-05-thin-line-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-05-thin-line-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/03-05-thin-line-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 93998
              },
              {
                "name": "sticker-centered-contact-v21.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/sticker-centered-contact-v21.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/sticker-centered-contact-v21.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21/sticker-centered-contact-v21.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 484179
              },
              {
                "name": "01-01-pictogram-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-01-pictogram-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-01-pictogram-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-01-pictogram-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 201002
              },
              {
                "name": "01-02-pictogram-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-02-pictogram-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-02-pictogram-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-02-pictogram-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 149181
              },
              {
                "name": "01-03-pictogram-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-03-pictogram-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-03-pictogram-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-03-pictogram-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 124577
              },
              {
                "name": "01-04-pictogram-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-04-pictogram-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-04-pictogram-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-04-pictogram-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 113611
              },
              {
                "name": "01-05-pictogram-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-05-pictogram-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-05-pictogram-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/01-05-pictogram-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 77792
              },
              {
                "name": "02-01-text-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-01-text-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-01-text-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-01-text-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 197766
              },
              {
                "name": "02-02-text-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-02-text-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-02-text-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-02-text-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 143619
              },
              {
                "name": "02-03-text-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-03-text-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-03-text-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-03-text-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 122346
              },
              {
                "name": "02-04-text-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-04-text-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-04-text-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-04-text-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 111431
              },
              {
                "name": "02-05-text-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-05-text-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-05-text-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/02-05-text-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 76125
              },
              {
                "name": "03-01-thin-line-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-01-thin-line-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-01-thin-line-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-01-thin-line-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 187646
              },
              {
                "name": "03-02-thin-line-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-02-thin-line-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-02-thin-line-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-02-thin-line-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 140509
              },
              {
                "name": "03-03-thin-line-left-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-03-thin-line-left-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-03-thin-line-left-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-03-thin-line-left-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 117216
              },
              {
                "name": "03-04-thin-line-right-35.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-04-thin-line-right-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-04-thin-line-right-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-04-thin-line-right-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 108509
              },
              {
                "name": "03-05-thin-line-low-15.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-05-thin-line-low-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-05-thin-line-low-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/03-05-thin-line-low-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 75244
              },
              {
                "name": "StickerMultiAngleApprovalPreview.png",
                "path": "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/StickerMultiAngleApprovalPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/StickerMultiAngleApprovalPreview.png",
                "url": "../../unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20/StickerMultiAngleApprovalPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 642643
              }
            ]
          },
          {
            "label": "Premium Display Case 中的全部三叶金属帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "展示盒各轮 Unity 输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 269671
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 404821
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 429667
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309727
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 416259
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 204168
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 322782
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 459362
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 474761
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 358191
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463236
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 237126
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 303518
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 429094
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 433113
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 337410
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 436903
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 225364
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 305529
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441578
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460755
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 346379
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452695
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 227603
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 311688
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 448731
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 466712
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 351991
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456607
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 231875
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 284303
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 419067
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 445569
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 327631
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437531
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 212105
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1794376
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1719170
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1565312
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1587224
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1654004
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1146378
              }
            ]
          }
        ]
      }
    },
    {
      "id": "gold-four-wing",
      "name": "镜钢四翼",
      "productId": "gold-four-wing",
      "status": "current",
      "statusLabel": "正式模型 · 输入溯源不足",
      "summary": "项目内缺少独立外部参考包；现有链条主要从导入模型直接进入 Unity，再反复修复轴心、轴圈、材质和展示比例。",
      "diagnosis": "这是典型的“有结果、缺输入依据”。重新生成前应补齐正交轮廓、侧面厚度、中心机构和真实尺寸参考，否则会继续依赖旧模型修补。",
      "rebuildFocus": [
        "补齐正/背/侧/顶正交参考",
        "锁定 85 mm 真实直径",
        "明确四翼而不是三翼的轮廓读法",
        "控制镜钢高光，避免白色剪切"
      ],
      "stages": {
        "input": [
          {
            "label": "当前仅存的导入模型 Hero",
            "folders": [
              "Artifacts/ImportedSpinner"
            ],
            "explicitFiles": [],
            "note": "没有发现对应的完整外部正交参考包。",
            "state": "working",
            "files": [
              {
                "name": "imported-spinner-hero.png",
                "path": "Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "url": "../../Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 319330
              }
            ]
          },
          {
            "label": "导入模型与纹理",
            "folders": [
              "unity/FidgetingApp/Assets/_ImportedSpinner"
            ],
            "explicitFiles": [],
            "note": "现有几何与材质的直接来源。",
            "state": "working",
            "files": [
              {
                "name": "DragonScaleEDC_CLI_85mm_Collision.fbx",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 68060
              },
              {
                "name": "DragonScaleEDC_CLI_85mm.fbx",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm.fbx",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Models/DragonScaleCLI/DragonScaleEDC_CLI_85mm.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 745468
              },
              {
                "name": "ImportedSpinner_Runtime.obj",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner_Runtime.obj",
                "kind": "model",
                "extension": "OBJ",
                "sizeBytes": 7092113
              },
              {
                "name": "ImportedSpinner.fbx",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner.fbx",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Models/ImportedSpinner.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 119618652
              },
              {
                "name": "texture_pbr_20250901_metallic_smoothness.png",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic_smoothness.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic_smoothness.png",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic_smoothness.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 10066905
              },
              {
                "name": "texture_pbr_20250901_metallic.png",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic.png",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_metallic.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 6051602
              },
              {
                "name": "texture_pbr_20250901_normal.png",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_normal.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_normal.png",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_normal.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3786510
              },
              {
                "name": "texture_pbr_20250901_roughness.png",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_roughness.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_roughness.png",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901_roughness.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3342289
              },
              {
                "name": "texture_pbr_20250901.png",
                "path": "unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901.png",
                "url": "../../unity/FidgetingApp/Assets/_ImportedSpinner/Textures/texture_pbr_20250901.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 16584806
              }
            ]
          }
        ],
        "process": [
          {
            "label": "恢复批准多角度",
            "folders": [
              "Artifacts/RecoveryApprovalV22"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、Left、Right、Low 和联系表。",
            "state": "working",
            "files": [
              {
                "name": "gold-four-wing-five-angle-contact.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-five-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-five-angle-contact.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-five-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1339770
              },
              {
                "name": "gold-four-wing-hero.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-hero.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 538475
              },
              {
                "name": "gold-four-wing-left.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-left.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 544470
              },
              {
                "name": "gold-four-wing-low.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-low.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515565
              },
              {
                "name": "gold-four-wing-right.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-right.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 512561
              },
              {
                "name": "gold-four-wing-top.png",
                "path": "Artifacts/RecoveryApprovalV22/gold-four-wing-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/gold-four-wing-top.png",
                "url": "../../Artifacts/RecoveryApprovalV22/gold-four-wing-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 562710
              },
              {
                "name": "build22-model-3-gold-four-wing.png",
                "path": "Artifacts/RecoveryApprovalV22/Native/build22-model-3-gold-four-wing.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/Native/build22-model-3-gold-four-wing.png",
                "url": "../../Artifacts/RecoveryApprovalV22/Native/build22-model-3-gold-four-wing.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3462943
              }
            ]
          },
          {
            "label": "轴圈移除验证",
            "folders": [
              "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing"
            ],
            "explicitFiles": [],
            "note": "移除额外 crown/bezel 后的 Unity 多视角。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 76924
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 137635
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 58545
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 69690
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 49661
              },
              {
                "name": "contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing/contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 62702
              }
            ]
          },
          {
            "label": "成长阶段材质图",
            "folders": [
              "Artifacts/ProgressionVisuals"
            ],
            "explicitFiles": [],
            "note": "等级材质变化，不代表新几何。",
            "state": "working",
            "files": [
              {
                "name": "gold-four-wing-lv001.png",
                "path": "Artifacts/ProgressionVisuals/gold-four-wing-lv001.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/gold-four-wing-lv001.png",
                "url": "../../Artifacts/ProgressionVisuals/gold-four-wing-lv001.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 326372
              },
              {
                "name": "gold-four-wing-lv020.png",
                "path": "Artifacts/ProgressionVisuals/gold-four-wing-lv020.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/gold-four-wing-lv020.png",
                "url": "../../Artifacts/ProgressionVisuals/gold-four-wing-lv020.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 338724
              },
              {
                "name": "gold-four-wing-lv050.png",
                "path": "Artifacts/ProgressionVisuals/gold-four-wing-lv050.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/gold-four-wing-lv050.png",
                "url": "../../Artifacts/ProgressionVisuals/gold-four-wing-lv050.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 341627
              },
              {
                "name": "gold-four-wing-lv075.png",
                "path": "Artifacts/ProgressionVisuals/gold-four-wing-lv075.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/gold-four-wing-lv075.png",
                "url": "../../Artifacts/ProgressionVisuals/gold-four-wing-lv075.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 348597
              },
              {
                "name": "gold-four-wing-lv100.png",
                "path": "Artifacts/ProgressionVisuals/gold-four-wing-lv100.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/gold-four-wing-lv100.png",
                "url": "../../Artifacts/ProgressionVisuals/gold-four-wing-lv100.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 343882
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Premium Display Case 中的全部四翼帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "各轮 Hero/Top/斜角/Low/Phone 输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 301309
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 428626
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460399
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 320135
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 432074
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224144
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 329264
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460869
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 489160
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 350073
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463403
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 243803
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 283933
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441905
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 425944
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 333518
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 438217
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 213045
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 325394
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455004
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 484288
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 345973
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460758
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 240094
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 326989
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 458186
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 486747
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 348667
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 461947
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 242068
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 314462
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441608
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476483
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 335228
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 449897
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232652
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1739788
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1686280
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1541443
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1550003
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1619504
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1113489
              }
            ]
          },
          {
            "label": "批准展示盒材质证据",
            "folders": [
              "unity/FidgetingApp/Docs/DesignBibleAssets"
            ],
            "explicitFiles": [],
            "note": "批准的是展示比例和材质响应，不是新的四翼几何。",
            "state": "approved",
            "files": [
              {
                "name": "collector-slab-materials-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 584439
              },
              {
                "name": "collector-slab-six-products-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              }
            ]
          }
        ]
      }
    },
    {
      "id": "graphite-two-lobe",
      "name": "石墨双叶",
      "productId": "graphite-two-lobe",
      "status": "current",
      "statusLabel": "正式模型 · 参考链较清晰",
      "summary": "独立结构参考 → 一体转子/凹面指盖/轴承爆炸 → Unity 真实比例与轴圈修复 → 展示盒输出。",
      "diagnosis": "现模型的问题主要不是机构，而是过于简单、容易读成普通塑料条。重做应增强精密倒角、侧壁分件和表面细节，同时保持 50 mm 小体量。",
      "rebuildFocus": [
        "保持约 50 × 24 × 18.68 mm",
        "一体双叶转子与固定指盖同轴",
        "增加可制造的边缘层次而非装饰圈",
        "保持石墨/珠砂金属而非纯黑塑料"
      ],
      "stages": {
        "input": [
          {
            "label": "双叶结构参考五张",
            "folders": [
              "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate"
            ],
            "explicitFiles": [],
            "note": "装配、转子、指盖、轴承/套筒和完整爆炸。",
            "state": "working",
            "files": [
              {
                "name": "01-assembled-reference.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/01-assembled-reference.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/01-assembled-reference.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/01-assembled-reference.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2025939
              },
              {
                "name": "02-one-piece-rotor-body.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/02-one-piece-rotor-body.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/02-one-piece-rotor-body.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/02-one-piece-rotor-body.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1818860
              },
              {
                "name": "03-concave-finger-cap.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/03-concave-finger-cap.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/03-concave-finger-cap.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/03-concave-finger-cap.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1961612
              },
              {
                "name": "04-bearing-and-sleeves.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/04-bearing-and-sleeves.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/04-bearing-and-sleeves.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/04-bearing-and-sleeves.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1639024
              },
              {
                "name": "05-full-axial-exploded.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/05-full-axial-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/05-full-axial-exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate/05-full-axial-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1777728
              }
            ]
          }
        ],
        "process": [
          {
            "label": "结构校正与爆炸概念",
            "folders": [
              "unity/FidgetingApp/Artifacts/TwoLobeBar"
            ],
            "explicitFiles": [],
            "note": "校正结构、爆炸图和 Hero。",
            "state": "working",
            "files": [
              {
                "name": "two-lobe-bar-corrected-structure-concept.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-corrected-structure-concept.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-corrected-structure-concept.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-corrected-structure-concept.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2108673
              },
              {
                "name": "two-lobe-bar-exploded.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 115063
              },
              {
                "name": "two-lobe-bar-hero.png",
                "path": "unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/TwoLobeBar/two-lobe-bar-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 174836
              }
            ]
          },
          {
            "label": "真实尺度修复",
            "folders": [
              "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix"
            ],
            "explicitFiles": [],
            "note": "用 50/85 比例修复 Library/详情 framing。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 158333
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 197002
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 153141
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 154112
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 149275
              },
              {
                "name": "contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix/contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 430439
              }
            ]
          },
          {
            "label": "轴圈移除验证",
            "folders": [
              "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe"
            ],
            "explicitFiles": [],
            "note": "清除额外可见轴圈后的多视角。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 158332
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 197002
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 153125
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 154112
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 149230
              },
              {
                "name": "contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe/contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 94849
              }
            ]
          }
        ],
        "output": [
          {
            "label": "恢复批准候选",
            "folders": [
              "Artifacts/RecoveryApprovalV22"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、Left、Right、Low 与联系表。",
            "state": "working",
            "files": [
              {
                "name": "graphite-two-lobe-five-angle-contact.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-five-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-five-angle-contact.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-five-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1179178
              },
              {
                "name": "graphite-two-lobe-hero.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-hero.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 512001
              },
              {
                "name": "graphite-two-lobe-left.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-left.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516844
              },
              {
                "name": "graphite-two-lobe-low.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-low.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 506272
              },
              {
                "name": "graphite-two-lobe-right.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-right.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 522141
              },
              {
                "name": "graphite-two-lobe-top.png",
                "path": "Artifacts/RecoveryApprovalV22/graphite-two-lobe-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/graphite-two-lobe-top.png",
                "url": "../../Artifacts/RecoveryApprovalV22/graphite-two-lobe-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 488761
              },
              {
                "name": "build22-model-4-graphite-two-lobe.png",
                "path": "Artifacts/RecoveryApprovalV22/Native/build22-model-4-graphite-two-lobe.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/Native/build22-model-4-graphite-two-lobe.png",
                "url": "../../Artifacts/RecoveryApprovalV22/Native/build22-model-4-graphite-two-lobe.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3106421
              }
            ]
          },
          {
            "label": "Premium Display Case 中的全部双叶帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "展示盒中的多轮真实 Unity 输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 267221
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 446024
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 434018
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 328506
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 426517
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 200268
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 292115
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477322
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 459313
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 356538
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456539
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217240
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 273001
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 446920
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 410431
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 332108
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 427188
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 204141
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 289014
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 472785
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456879
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 353049
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 453756
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214395
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 291238
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 475682
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 458581
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 355847
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455236
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 216269
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 277089
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460100
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 447848
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 342061
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 443692
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 207754
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1722872
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1679004
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1502647
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1549687
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1603442
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1102621
              }
            ]
          },
          {
            "label": "批准展示盒材质证据",
            "folders": [
              "unity/FidgetingApp/Docs/DesignBibleAssets"
            ],
            "explicitFiles": [],
            "note": "当前批准的喷砂/磨砂金属响应。",
            "state": "approved",
            "files": [
              {
                "name": "collector-slab-materials-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 584439
              },
              {
                "name": "collector-slab-six-products-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              }
            ]
          }
        ]
      }
    },
    {
      "id": "blue-classic",
      "name": "经典蓝色",
      "productId": "blue-classic",
      "status": "current",
      "statusLabel": "正式模型 · 溯源缺口最大",
      "summary": "项目中保留正式 Unity 场景、缩略图和成长/环境输出，但没有找到与其他模型同等级的输入参考、爆炸图和 Blender 多角度链。",
      "diagnosis": "如果准备重新生成，不能只拿现有缩略图反推。应先补一套真实尺寸、中心轴承、指盖、三叶厚度与背面结构参考。",
      "rebuildFocus": [
        "新增五视图与轴向爆炸输入",
        "保留最易理解的经典三叶身份",
        "明确蓝色金属而非蓝色塑料",
        "与正式触控/轴心系统保持一致"
      ],
      "stages": {
        "input": [
          {
            "label": "输入参考缺失说明",
            "folders": [],
            "explicitFiles": [
              "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"
            ],
            "note": "目前主要依赖设计圣经中的产品约束，没有专属图片参考包。",
            "state": "working",
            "files": [
              {
                "name": "FidgetingAppProductDesignBible.md",
                "path": "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
                "url": "../../unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
                "kind": "document",
                "extension": "MD",
                "sizeBytes": 205595
              }
            ]
          }
        ],
        "process": [
          {
            "label": "成长阶段输出",
            "folders": [
              "Artifacts/ProgressionVisuals"
            ],
            "explicitFiles": [],
            "note": "不同等级材质/环境呈现。",
            "state": "working",
            "files": [
              {
                "name": "blue-classic-lv001.png",
                "path": "Artifacts/ProgressionVisuals/blue-classic-lv001.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/blue-classic-lv001.png",
                "url": "../../Artifacts/ProgressionVisuals/blue-classic-lv001.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441347
              },
              {
                "name": "blue-classic-lv020.png",
                "path": "Artifacts/ProgressionVisuals/blue-classic-lv020.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/blue-classic-lv020.png",
                "url": "../../Artifacts/ProgressionVisuals/blue-classic-lv020.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 400853
              },
              {
                "name": "blue-classic-lv050.png",
                "path": "Artifacts/ProgressionVisuals/blue-classic-lv050.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/blue-classic-lv050.png",
                "url": "../../Artifacts/ProgressionVisuals/blue-classic-lv050.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 402261
              },
              {
                "name": "blue-classic-lv075.png",
                "path": "Artifacts/ProgressionVisuals/blue-classic-lv075.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/blue-classic-lv075.png",
                "url": "../../Artifacts/ProgressionVisuals/blue-classic-lv075.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 404607
              },
              {
                "name": "blue-classic-lv100.png",
                "path": "Artifacts/ProgressionVisuals/blue-classic-lv100.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ProgressionVisuals/blue-classic-lv100.png",
                "url": "../../Artifacts/ProgressionVisuals/blue-classic-lv100.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 413397
              }
            ]
          },
          {
            "label": "旧环境集成图",
            "folders": [
              "Artifacts/EnvironmentIntegration"
            ],
            "explicitFiles": [],
            "note": "模型在场景中的构图，不是建模输入。",
            "state": "working",
            "files": [
              {
                "name": "blue-classic-parallax-unity.png",
                "path": "Artifacts/EnvironmentIntegration/blue-classic-parallax-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EnvironmentIntegration/blue-classic-parallax-unity.png",
                "url": "../../Artifacts/EnvironmentIntegration/blue-classic-parallax-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1980501
              },
              {
                "name": "blue-classic-unity.png",
                "path": "Artifacts/EnvironmentIntegration/blue-classic-unity.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/EnvironmentIntegration/blue-classic-unity.png",
                "url": "../../Artifacts/EnvironmentIntegration/blue-classic-unity.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1990376
              }
            ]
          }
        ],
        "output": [
          {
            "label": "原生模型缩略图",
            "folders": [
              "unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models"
            ],
            "explicitFiles": [],
            "note": "目录使用的小尺寸输出。",
            "state": "working",
            "files": [
              {
                "name": "product-thumbnail-blue-classic.png",
                "path": "unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-blue-classic.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-blue-classic.png",
                "url": "../../unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-blue-classic.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 431777
              }
            ]
          },
          {
            "label": "分模型壁纸与环境输出",
            "folders": [
              "unity/FidgetingApp/Assets/Plugins/iOS/SceneWallpapers",
              "unity/FidgetingApp/Artifacts/AdaptiveBackdropPreview"
            ],
            "explicitFiles": [],
            "note": "当前环境中的模型呈现。",
            "state": "working",
            "files": []
          }
        ]
      }
    },
    {
      "id": "dragon-scale-edc",
      "name": "龙鳞 EDC",
      "productId": "candidate-dragon-scale",
      "status": "candidate",
      "statusLabel": "候选模型 · 不应新增第七槽位",
      "summary": "Novo 实物视频帧 → 生成四视图 → Rodin 原始网格/Blender cleanup/CLIAnything 重建 → Unity shipping 候选和轴心修复。",
      "diagnosis": "这是输入到输出最容易直观看出“形似但不够精密”的一条链。当前生成结果的翼片厚度、中心盖尺度、切面节奏与真实参考仍有明显差异。",
      "rebuildFocus": [
        "以实物视频的掌中尺度和侧厚为主",
        "同一份 CAD-like 基础生成所有视图",
        "中心盖不要过大遮住翼片根部",
        "保留切面语言但减少 AI 融化边缘"
      ],
      "stages": {
        "input": [
          {
            "label": "Novo Dragon Scale 实物视频帧",
            "folders": [
              "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames"
            ],
            "explicitFiles": [],
            "note": "掌中尺度、正面、中心切面、握持、侧面和平衡。",
            "state": "working",
            "files": [
              {
                "name": "00_contact_sheet.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/00_contact_sheet.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/00_contact_sheet.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/00_contact_sheet.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 250028
              },
              {
                "name": "01_product_in_palm_03.5s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/01_product_in_palm_03.5s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/01_product_in_palm_03.5s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/01_product_in_palm_03.5s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 129331
              },
              {
                "name": "02_airflow_spin_setup_08.5s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/02_airflow_spin_setup_08.5s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/02_airflow_spin_setup_08.5s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/02_airflow_spin_setup_08.5s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 124261
              },
              {
                "name": "03_front_hero_10.5s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/03_front_hero_10.5s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/03_front_hero_10.5s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/03_front_hero_10.5s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 98619
              },
              {
                "name": "04_faceted_center_detail_12.5s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/04_faceted_center_detail_12.5s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/04_faceted_center_detail_12.5s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/04_faceted_center_detail_12.5s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 116244
              },
              {
                "name": "05_pinch_grip_15.0s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/05_pinch_grip_15.0s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/05_pinch_grip_15.0s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/05_pinch_grip_15.0s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 117090
              },
              {
                "name": "06_freewheel_motion_18.5s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/06_freewheel_motion_18.5s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/06_freewheel_motion_18.5s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/06_freewheel_motion_18.5s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 97411
              },
              {
                "name": "07_side_flick_grip_27.0s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/07_side_flick_grip_27.0s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/07_side_flick_grip_27.0s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/07_side_flick_grip_27.0s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 96478
              },
              {
                "name": "08_side_profile_30.0s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/08_side_profile_30.0s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/08_side_profile_30.0s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/08_side_profile_30.0s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 117583
              },
              {
                "name": "09_fingertip_balance_33.0s.jpg",
                "path": "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/09_fingertip_balance_33.0s.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/09_fingertip_balance_33.0s.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames/09_fingertip_balance_33.0s.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 97776
              }
            ]
          }
        ],
        "process": [
          {
            "label": "生成的龙鳞四视图",
            "folders": [
              "Artifacts/龙鳞EDC_四视图"
            ],
            "explicitFiles": [],
            "note": "基础灰银与金色点缀两组；作为目标图而非制造图。",
            "state": "working",
            "files": [
              {
                "name": "龙鳞EDC_背面图_高级合金金色点缀.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图_高级合金金色点缀.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图_高级合金金色点缀.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图_高级合金金色点缀.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1966622
              },
              {
                "name": "龙鳞EDC_背面图.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_背面图.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2077323
              },
              {
                "name": "龙鳞EDC_右侧图_高级合金金色点缀.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图_高级合金金色点缀.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图_高级合金金色点缀.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图_高级合金金色点缀.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1368106
              },
              {
                "name": "龙鳞EDC_右侧图.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_右侧图.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1488606
              },
              {
                "name": "龙鳞EDC_主视图_高级合金金色点缀.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图_高级合金金色点缀.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图_高级合金金色点缀.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图_高级合金金色点缀.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1873495
              },
              {
                "name": "龙鳞EDC_主视图.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_主视图.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 2114825
              },
              {
                "name": "龙鳞EDC_左侧图_高级合金金色点缀.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图_高级合金金色点缀.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图_高级合金金色点缀.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图_高级合金金色点缀.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1516105
              },
              {
                "name": "龙鳞EDC_左侧图.png",
                "path": "Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图.png",
                "url": "../../Artifacts/龙鳞EDC_四视图/龙鳞EDC_左侧图.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1636695
              }
            ]
          },
          {
            "label": "Rodin raw / Blender cleanup 对照",
            "folders": [
              "unity/FidgetingApp/Artifacts/BlenderDragonScale"
            ],
            "explicitFiles": [],
            "note": "原始、Blender 和 cleanup 三阶段多角度对照。",
            "state": "working",
            "files": [
              {
                "name": "dragon-scale-edc-exploded.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 488934
              },
              {
                "name": "dragon-scale-edc-hero.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 516691
              },
              {
                "name": "dragon-scale-edc-side.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-side.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 338106
              },
              {
                "name": "dragon-scale-edc-top.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-top.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/dragon-scale-edc-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 453590
              },
              {
                "name": "DragonScaleEDC_Rodin_bottom_iso.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_bottom_iso.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_bottom_iso.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_bottom_iso.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 361438
              },
              {
                "name": "DragonScaleEDC_Rodin_iso.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_iso.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_iso.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_iso.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 372499
              },
              {
                "name": "DragonScaleEDC_Rodin_side.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_side.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 376951
              },
              {
                "name": "DragonScaleEDC_Rodin_top.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Blender/DragonScaleEDC_Rodin_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 493817
              },
              {
                "name": "DragonScaleEDC_Cleanup_exploded.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 535805
              },
              {
                "name": "DragonScaleEDC_Cleanup_iso.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_iso.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_iso.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_iso.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 507114
              },
              {
                "name": "DragonScaleEDC_Cleanup_side.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_side.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 416144
              },
              {
                "name": "DragonScaleEDC_Cleanup_top.png",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/Cleanup/DragonScaleEDC_Cleanup_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 621027
              },
              {
                "name": "preview.webp",
                "path": "unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/raw/preview.webp",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/raw/preview.webp",
                "url": "../../unity/FidgetingApp/Artifacts/BlenderDragonScale/Rodin/raw/preview.webp",
                "kind": "image",
                "extension": "WEBP",
                "sizeBytes": 3888
              }
            ]
          },
          {
            "label": "可编辑源与导出",
            "folders": [
              "unity/FidgetingApp/ArtSource/DragonScaleEDC"
            ],
            "explicitFiles": [],
            "note": "Rodin、CLIAnything 与手工清理版本。",
            "state": "working",
            "files": [
              {
                "name": "DragonScaleEDC_CLI_85mm_Collision.fbx",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm_Collision.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 68060
              },
              {
                "name": "DragonScaleEDC_CLI_85mm.blend",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.blend",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 564860
              },
              {
                "name": "DragonScaleEDC_CLI_85mm.fbx",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.fbx",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 745468
              },
              {
                "name": "DragonScaleEDC_CLI_85mm.glb",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.glb",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.glb",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI_85mm.glb",
                "kind": "model",
                "extension": "GLB",
                "sizeBytes": 713732
              },
              {
                "name": "DragonScaleEDC.blend",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/DragonScaleEDC.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/DragonScaleEDC.blend",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/DragonScaleEDC.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 651053
              },
              {
                "name": "DragonScaleEDC_Rodin_Cleanup.blend",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.blend",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 1976436
              },
              {
                "name": "DragonScaleEDC_Rodin_Cleanup.glb",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.glb",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.glb",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.glb",
                "kind": "model",
                "extension": "GLB",
                "sizeBytes": 1532272
              },
              {
                "name": "DragonScaleEDC_Rodin_Raw.blend",
                "path": "unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Raw.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Raw.blend",
                "url": "../../unity/FidgetingApp/ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Raw.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 1925156
              }
            ]
          }
        ],
        "output": [
          {
            "label": "CLIAnything 多角度与爆炸",
            "folders": [
              "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、左右斜角、Low、Side、Exploded。",
            "state": "working",
            "files": [
              {
                "name": "dragon-scale-cli-exploded.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1439901
              },
              {
                "name": "dragon-scale-cli-hero.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1736987
              },
              {
                "name": "dragon-scale-cli-left-oblique.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-left-oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-left-oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-left-oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1625191
              },
              {
                "name": "dragon-scale-cli-low.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-low.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1117635
              },
              {
                "name": "dragon-scale-cli-right-oblique.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-right-oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-right-oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-right-oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1647207
              },
              {
                "name": "dragon-scale-cli-side.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-side.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 732686
              },
              {
                "name": "dragon-scale-cli-top.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-top.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1694636
              }
            ]
          },
          {
            "label": "Unity shipping 候选",
            "folders": [
              "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview"
            ],
            "explicitFiles": [],
            "note": "正式场景中的多角度输出。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 84243
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 153961
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 61125
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 72132
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 50727
              }
            ]
          },
          {
            "label": "轴心居中修复",
            "folders": [
              "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix"
            ],
            "explicitFiles": [],
            "note": "修复中心 pivot 后的六视角。",
            "state": "working",
            "files": [
              {
                "name": "01-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/01-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/01-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/01-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 72202
              },
              {
                "name": "02-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/02-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/02-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/02-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 154530
              },
              {
                "name": "03-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/03-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/03-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/03-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 62726
              },
              {
                "name": "04-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/04-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/04-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/04-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 72626
              },
              {
                "name": "05-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/05-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/05-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/05-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 50743
              },
              {
                "name": "contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix/contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 339038
              }
            ]
          }
        ]
      }
    },
    {
      "id": "unbound-slider",
      "name": "Unbound Slider",
      "productId": "rejected-unbound-slider",
      "status": "rejected",
      "statusLabel": "已拒绝候选 · 可借鉴流程",
      "summary": "共享推牌输入 → 两轮白模和细节设计 → CLIAnything 重建 → Unity Round 5；最终 shipping 预览已明确拒绝。",
      "diagnosis": "白模阶段暴露了主要问题：两排外露圆件过多、正面像控制面板、层级厚重，缺少真正高级 EDC 的克制与机械可信度。",
      "rebuildFocus": [
        "不要复用 Round 5 外观",
        "可保留分层/爆炸工作流",
        "减少外露磁体和装饰孔",
        "重新定义拇指接触面与滑动方向"
      ],
      "stages": {
        "input": [
          {
            "label": "共享的 KOVO / Matrix / 专利参考",
            "folders": [
              "unity/FidgetingApp/Docs/References/PushCardModeling"
            ],
            "explicitFiles": [],
            "note": "外轮廓、掌中尺度、层级、轨道与磁体。",
            "state": "working",
            "files": [
              {
                "name": "01_kovo_transparent_internal_front.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/01_kovo_transparent_internal_front.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 100062
              },
              {
                "name": "02_kovo_smoke_internal_track_closeup.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/02_kovo_smoke_internal_track_closeup.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 74969
              },
              {
                "name": "03_kovo_thumb_grip.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/03_kovo_thumb_grip.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 115415
              },
              {
                "name": "04_matrix_limite_slide_grip.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/04_matrix_limite_slide_grip.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 67368
              },
              {
                "name": "05_matrix_limite_palm_scale.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/05_matrix_limite_palm_scale.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 82630
              },
              {
                "name": "06_matrix_limite_dual_backplate.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/06_matrix_limite_dual_backplate.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 88343
              },
              {
                "name": "07_tita_pro_layered_body.jpg",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/07_tita_pro_layered_body.jpg",
                "kind": "image",
                "extension": "JPG",
                "sizeBytes": 94288
              },
              {
                "name": "08_usd1020916_perspective.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/08_usd1020916_perspective.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 291279
              },
              {
                "name": "09_usd1020916_front.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/09_usd1020916_front.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 210017
              },
              {
                "name": "10_usd1020916_rear.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/10_usd1020916_rear.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 115467
              },
              {
                "name": "11_usd1020916_side.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/11_usd1020916_side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 118475
              },
              {
                "name": "12_usd1020916_exploded_front.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/12_usd1020916_exploded_front.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 310989
              },
              {
                "name": "13_usd1020916_exploded_perspective.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/13_usd1020916_exploded_perspective.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224197
              },
              {
                "name": "14_cn218011061_internal_tracks_magnets.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/14_cn218011061_internal_tracks_magnets.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 919237
              },
              {
                "name": "15_cn218011061_replaceable_panel.png",
                "path": "unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "url": "../../unity/FidgetingApp/Docs/References/PushCardModeling/15_cn218011061_replaceable_panel.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 223426
              }
            ]
          }
        ],
        "process": [
          {
            "label": "第一轮白模六视图",
            "folders": [
              "Artifacts/UnboundSlider/WhiteModel_2026-08-10"
            ],
            "explicitFiles": [],
            "note": "装配、爆炸、正视、斜角、Low、Top。",
            "state": "working",
            "files": [
              {
                "name": "01_AssembledHero.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/01_AssembledHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/01_AssembledHero.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/01_AssembledHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 749349
              },
              {
                "name": "02_ExplodedHero.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/02_ExplodedHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/02_ExplodedHero.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/02_ExplodedHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 769142
              },
              {
                "name": "03_FrontPlan.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/03_FrontPlan.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/03_FrontPlan.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/03_FrontPlan.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 703195
              },
              {
                "name": "04_LeftOblique.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/04_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/04_LeftOblique.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/04_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 742331
              },
              {
                "name": "05_LowAngle.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/05_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/05_LowAngle.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/05_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 512828
              },
              {
                "name": "06_TopAngle.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-10/06_TopAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-10/06_TopAngle.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-10/06_TopAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 856529
              }
            ]
          },
          {
            "label": "第二轮细节白模",
            "folders": [
              "Artifacts/UnboundSlider/WhiteModel_2026-08-11"
            ],
            "explicitFiles": [],
            "note": "细节 Hero、正面图案与装饰版本。",
            "state": "working",
            "files": [
              {
                "name": "07_DetailFront.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailFront.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailFront.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailFront.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 708356
              },
              {
                "name": "07_DetailHero.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailHero.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-11/07_DetailHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 731830
              },
              {
                "name": "08_DetailExploded.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-11/08_DetailExploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-11/08_DetailExploded.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-11/08_DetailExploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 786190
              },
              {
                "name": "09_MiddlePatternFront.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-11/09_MiddlePatternFront.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-11/09_MiddlePatternFront.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-11/09_MiddlePatternFront.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 659829
              },
              {
                "name": "10_OrnamentalFront.png",
                "path": "Artifacts/UnboundSlider/WhiteModel_2026-08-11/10_OrnamentalFront.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/UnboundSlider/WhiteModel_2026-08-11/10_OrnamentalFront.png",
                "url": "../../Artifacts/UnboundSlider/WhiteModel_2026-08-11/10_OrnamentalFront.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 690166
              }
            ]
          },
          {
            "label": "CLIAnything 多角度/爆炸/开合",
            "folders": [
              "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything"
            ],
            "explicitFiles": [],
            "note": "重建后的 9 张结构输出。",
            "state": "working",
            "files": [
              {
                "name": "01_Top.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/01_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/01_Top.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/01_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1204688
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/02_AuthoredHero.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1302181
              },
              {
                "name": "03_LeftOblique.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/03_LeftOblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1301401
              },
              {
                "name": "04_RightOblique.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/04_RightOblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1335494
              },
              {
                "name": "05_LowAngle.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/05_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/05_LowAngle.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/05_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1174392
              },
              {
                "name": "06_Side.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/06_Side.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/06_Side.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/06_Side.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1038093
              },
              {
                "name": "07_Exploded.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/07_Exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/07_Exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/07_Exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1350353
              },
              {
                "name": "08_GoggleDetail.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/08_GoggleDetail.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/08_GoggleDetail.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/08_GoggleDetail.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1227392
              },
              {
                "name": "09_OpenTravel.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/09_OpenTravel.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/09_OpenTravel.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/09_OpenTravel.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1296106
              }
            ]
          },
          {
            "label": "Blender/FBX/GLB 源",
            "folders": [
              "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything"
            ],
            "explicitFiles": [],
            "note": "可编辑源、碰撞和纹理。",
            "state": "working",
            "files": [
              {
                "name": "T_Unbound_BrushedNormal.png",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_BrushedNormal.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_BrushedNormal.png",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_BrushedNormal.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1854
              },
              {
                "name": "T_Unbound_MetallicSmoothness.png",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_MetallicSmoothness.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_MetallicSmoothness.png",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/T_Unbound_MetallicSmoothness.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1854
              },
              {
                "name": "UnboundSlider_CLI_Collision.fbx",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI_Collision.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI_Collision.fbx",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI_Collision.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 21724
              },
              {
                "name": "UnboundSlider_CLI.blend",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.blend",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 668888
              },
              {
                "name": "UnboundSlider_CLI.fbx",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.fbx",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 1758828
              },
              {
                "name": "UnboundSlider_CLI.glb",
                "path": "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.glb",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.glb",
                "url": "../../unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSlider_CLI.glb",
                "kind": "model",
                "extension": "GLB",
                "sizeBytes": 3061616
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Unity shipping Round 5（已拒绝）",
            "folders": [
              "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11"
            ],
            "explicitFiles": [],
            "note": "Library、Hero、左右斜角、Top、Low 和内部打开视角。",
            "state": "rejected",
            "files": [
              {
                "name": "01_LibraryPreview.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/01_LibraryPreview.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/01_LibraryPreview.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/01_LibraryPreview.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3942922
              },
              {
                "name": "02_AuthoredHero.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/02_AuthoredHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/02_AuthoredHero.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/02_AuthoredHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3943043
              },
              {
                "name": "03_LeftOblique.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/03_LeftOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/03_LeftOblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/03_LeftOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4161671
              },
              {
                "name": "04_RightOblique.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/04_RightOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/04_RightOblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/04_RightOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4148104
              },
              {
                "name": "05_Top.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/05_Top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/05_Top.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/05_Top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3894490
              },
              {
                "name": "06_LowAngle.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/06_LowAngle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/06_LowAngle.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/06_LowAngle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3960622
              },
              {
                "name": "07_OpenInteriorHero.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/07_OpenInteriorHero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/07_OpenInteriorHero.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/07_OpenInteriorHero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3893383
              },
              {
                "name": "08_OpenInteriorOblique.png",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/08_OpenInteriorOblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/08_OpenInteriorOblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/08_OpenInteriorOblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4037625
              },
              {
                "name": "AxisFixedCandidate_EditModeTests_10of10.xml",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/AxisFixedCandidate_EditModeTests_10of10.xml",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/AxisFixedCandidate_EditModeTests_10of10.xml",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/AxisFixedCandidate_EditModeTests_10of10.xml",
                "kind": "document",
                "extension": "XML",
                "sizeBytes": 10942
              },
              {
                "name": "UnityShippingPreview.log",
                "path": "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/UnityShippingPreview.log",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/UnityShippingPreview.log",
                "url": "../../unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/UnityShippingPreview.log",
                "kind": "document",
                "extension": "LOG",
                "sizeBytes": 49612
              }
            ]
          }
        ]
      }
    },
    {
      "id": "pointed-three-blade",
      "name": "尖角三叶 / Edge Triad",
      "productId": "historical-pointed-three-blade",
      "status": "historical",
      "statusLabel": "历史 catalog 候选",
      "summary": "Meshy/导入模型 → 单张 Hero → Recovery 多角度 → Cyberpunk 与 Premium Display Case 大量实际 Unity 输出。",
      "diagnosis": "图像很多，但建模输入很少；尖锐多边形轮廓在小尺寸下显得生硬。它还与设计圣经中的 blue-classic 首槽位存在 catalog 身份混用。",
      "rebuildFocus": [
        "先决定是否保留此 catalog 身份",
        "不要从场景截图反推网格",
        "补齐背面、厚度与轴承结构",
        "若淘汰，应清理展示盒中的历史命名"
      ],
      "stages": {
        "input": [
          {
            "label": "Meshy 导入资产",
            "folders": [
              "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257"
            ],
            "explicitFiles": [],
            "note": "当前能追溯到的生成输入/网格和纹理。",
            "state": "working",
            "files": [
              {
                "name": "Meshy_AI_Faceted_Triad_Emblem_0803124324_texture.fbx",
                "path": "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/Meshy_AI_Faceted_Triad_Emblem_0803124324_texture.fbx",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/Meshy_AI_Faceted_Triad_Emblem_0803124324_texture.fbx",
                "url": "../../unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/Meshy_AI_Faceted_Triad_Emblem_0803124324_texture.fbx",
                "kind": "model",
                "extension": "FBX",
                "sizeBytes": 64888412
              },
              {
                "name": "meshy_basecolor.png",
                "path": "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_basecolor.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_basecolor.png",
                "url": "../../unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_basecolor.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 43722163
              },
              {
                "name": "meshy_metallic_smoothness.png",
                "path": "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_metallic_smoothness.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_metallic_smoothness.png",
                "url": "../../unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_metallic_smoothness.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 3563470
              },
              {
                "name": "meshy_normal.png",
                "path": "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_normal.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_normal.png",
                "url": "../../unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257/meshy_normal.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 11155266
              }
            ]
          }
        ],
        "process": [
          {
            "label": "导入模型 Hero",
            "folders": [
              "Artifacts/ImportedSpinner"
            ],
            "explicitFiles": [],
            "note": "早期透明背景/独立 Hero。",
            "state": "working",
            "files": [
              {
                "name": "imported-spinner-hero.png",
                "path": "Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "url": "../../Artifacts/ImportedSpinner/imported-spinner-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 319330
              }
            ]
          },
          {
            "label": "Recovery 五角度",
            "folders": [
              "Artifacts/RecoveryApprovalV22"
            ],
            "explicitFiles": [],
            "note": "Hero、Top、Left、Right、Low 和联系表。",
            "state": "working",
            "files": [
              {
                "name": "pointed-three-blade-five-angle-contact.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-five-angle-contact.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-five-angle-contact.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-five-angle-contact.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1162466
              },
              {
                "name": "pointed-three-blade-hero.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-hero.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 530961
              },
              {
                "name": "pointed-three-blade-left.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-left.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 521064
              },
              {
                "name": "pointed-three-blade-low.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-low.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-low.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-low.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 515043
              },
              {
                "name": "pointed-three-blade-right.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-right.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 520036
              },
              {
                "name": "pointed-three-blade-top.png",
                "path": "Artifacts/RecoveryApprovalV22/pointed-three-blade-top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/RecoveryApprovalV22/pointed-three-blade-top.png",
                "url": "../../Artifacts/RecoveryApprovalV22/pointed-three-blade-top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 522485
              }
            ]
          }
        ],
        "output": [
          {
            "label": "Cyberpunk V5–V13 Unity 输出",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "九轮场景中的多角度真实模型；主要验证场景，不等于几何批准。",
            "state": "working",
            "files": [
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623361
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1624774
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1620417
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623338
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1616676
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1614085
              },
              {
                "name": "cyber-blue-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/cyber-blue-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/cyber-blue-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV5/cyber-blue-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4475590
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623361
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1624933
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1620525
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623397
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1616493
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1614138
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV6/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4471108
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623361
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1624933
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1620525
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1623397
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1616493
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1614138
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV7/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4471108
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1615610
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1622246
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1615580
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1624702
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1613041
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1612676
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV8/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4495256
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1653131
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1658300
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1653153
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1661637
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1649521
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1649606
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV9/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4610713
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1658837
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1659906
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1659255
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1658051
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1652127
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1649228
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV10/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4551686
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1682173
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1684304
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1682385
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1683186
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1676198
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1674243
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV11/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4571553
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1266483
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1270089
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1266265
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1271246
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1258986
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1254901
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV12/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4203045
              },
              {
                "name": "01-library-hero.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/01-library-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/01-library-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/01-library-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1436167
              },
              {
                "name": "02-authored-hero-42.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/02-authored-hero-42.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/02-authored-hero-42.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/02-authored-hero-42.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1442930
              },
              {
                "name": "03-top-89.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/03-top-89.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/03-top-89.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/03-top-89.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1435998
              },
              {
                "name": "04-left-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/04-left-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/04-left-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/04-left-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1443234
              },
              {
                "name": "05-right-oblique-35.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/05-right-oblique-35.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/05-right-oblique-35.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/05-right-oblique-35.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1433180
              },
              {
                "name": "06-low-angle-15.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/06-low-angle-15.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/06-low-angle-15.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/06-low-angle-15.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1433604
              },
              {
                "name": "cyber-pointed-spinner-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/cyber-pointed-spinner-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/cyber-pointed-spinner-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/CyberpunkEnvironmentUnityPreviewV13/cyber-pointed-spinner-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 4202873
              }
            ]
          },
          {
            "label": "Premium Display Case 中的全部尖角三叶帧",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "展示盒各轮 Unity 输出。",
            "state": "working",
            "files": [
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 289935
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 402830
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 427478
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 307257
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 414819
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 197266
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 281123
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 451706
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 465150
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 351864
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452265
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 228523
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309738
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 420272
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 419106
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 328165
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 424304
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 220375
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 258138
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 430756
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452287
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 334113
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441528
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214068
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 263064
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437124
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456283
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 338639
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 443471
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217843
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 297045
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 413887
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437016
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 320151
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 426779
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 203550
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1796022
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1711794
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1559235
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1595732
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1661905
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1145610
              }
            ]
          },
          {
            "label": "批准展示盒六产品总览中的 Edge Triad",
            "folders": [],
            "explicitFiles": [
              "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png"
            ],
            "note": "只表示该展示总览曾被批准；catalog 身份仍需与 blue-classic 统一。",
            "state": "approved",
            "files": [
              {
                "name": "collector-slab-six-products-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              }
            ]
          }
        ]
      }
    },
    {
      "id": "premium-display-case",
      "name": "Premium Display Case",
      "productId": "premium-display-case",
      "status": "current",
      "statusLabel": "正式展示容器 · 可独立重做",
      "summary": "Blender 展示盒结构 → 爆炸/灯光/材质 → 六款玩具在统一 content slot 中的 Hero、Top、斜角、Low 与 Phone 输出。",
      "diagnosis": "它不是玩具本体，但会显著放大模型的丑点。重新做玩具时应保留统一 content slot 和真实 bounds framing，避免为每款模型单独造假尺寸。",
      "rebuildFocus": [
        "保留一个统一 prefab 与 content slot",
        "模型占可见舱宽约 68–72%",
        "盒体材质退后，让玩具成为主角",
        "铭牌与稀有度不能遮挡真实几何"
      ],
      "stages": {
        "input": [
          {
            "label": "展示盒 Blender 源",
            "folders": [
              "unity/FidgetingApp/ArtSource/DisplayCase"
            ],
            "explicitFiles": [],
            "note": "统一展示容器的可编辑源。",
            "state": "working",
            "files": [
              {
                "name": "PremiumDisplayCase.blend",
                "path": "unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend",
                "url": "../../unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 177860
              }
            ]
          },
          {
            "label": "CLI Trinity Case 源",
            "folders": [
              "unity/FidgetingApp/ArtSource/CliAnythingTrinityCase"
            ],
            "explicitFiles": [],
            "note": "另一条展示壳体实验链。",
            "state": "working",
            "files": [
              {
                "name": "TrinityCaseCLI.blend",
                "path": "unity/FidgetingApp/ArtSource/CliAnythingTrinityCase/TrinityCaseCLI.blend",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/CliAnythingTrinityCase/TrinityCaseCLI.blend",
                "url": "../../unity/FidgetingApp/ArtSource/CliAnythingTrinityCase/TrinityCaseCLI.blend",
                "kind": "model",
                "extension": "BLEND",
                "sizeBytes": 222069
              }
            ]
          }
        ],
        "process": [
          {
            "label": "Blender 多角度",
            "folders": [
              "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview"
            ],
            "explicitFiles": [],
            "note": "展示盒本体的 Hero、正交和斜角。",
            "state": "working",
            "files": [
              {
                "name": "01_blender_assembled_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1737790
              },
              {
                "name": "02_blender_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1683905
              },
              {
                "name": "03_blender_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1749693
              },
              {
                "name": "04_blender_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1776356
              },
              {
                "name": "05_blender_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1765618
              },
              {
                "name": "06_blender_exploded_transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1301892
              },
              {
                "name": "blender-assembled-hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1418130
              },
              {
                "name": "blender-exploded-transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 938675
              }
            ]
          },
          {
            "label": "结构爆炸",
            "folders": [
              "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded"
            ],
            "explicitFiles": [],
            "note": "上盖、铭牌、舱体与底座层级。",
            "state": "working",
            "files": [
              {
                "name": "acrylic-case-exploded-chroma.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1642817
              },
              {
                "name": "acrylic-case-exploded-transparent-v2.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1108713
              },
              {
                "name": "acrylic-case-exploded-transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 401957
              }
            ]
          },
          {
            "label": "灯光与材质调色板",
            "folders": [
              "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview"
            ],
            "explicitFiles": [],
            "note": "不同材质与灯光响应。",
            "state": "working",
            "files": [
              {
                "name": "01_soft-neutral_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 414952
              },
              {
                "name": "01_soft-neutral_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 163613
              },
              {
                "name": "01_soft-neutral_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 323715
              },
              {
                "name": "02_rose-studio_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 407475
              },
              {
                "name": "02_rose-studio_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 198916
              },
              {
                "name": "02_rose-studio_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 316039
              },
              {
                "name": "03_amber-gallery_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 387448
              },
              {
                "name": "03_amber-gallery_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 184485
              },
              {
                "name": "03_amber-gallery_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309820
              },
              {
                "name": "04_cool-mist_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 394522
              },
              {
                "name": "04_cool-mist_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 189771
              },
              {
                "name": "04_cool-mist_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 312810
              },
              {
                "name": "display-case-lighting-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 359748
              }
            ]
          }
        ],
        "output": [
          {
            "label": "全部 Premium Display Case 预览",
            "folders": [
              "unity/FidgetingApp/Artifacts"
            ],
            "explicitFiles": [],
            "note": "包含全部模型、Badge、Laser、识别、基线一致性和材质迭代。",
            "state": "working",
            "files": [
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 838665
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 164488
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 301309
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 428626
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460399
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 320135
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 432074
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224144
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 267221
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 446024
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 434018
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 328506
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 426517
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 200268
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 304274
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 489011
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 447433
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 369507
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476168
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 224681
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 288481
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 449003
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452234
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 336483
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 445303
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214242
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 269671
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 404821
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 429667
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309727
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 416259
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 204168
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 289935
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 402830
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 427478
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 307257
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 414819
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseAllProductsPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 197266
              },
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 957520
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 250849
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 329264
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460869
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 489160
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 350073
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463403
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 243803
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 292115
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477322
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 459313
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 356538
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456539
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217240
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 358793
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 540853
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 490199
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 415873
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 518743
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 258618
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 317181
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 483436
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 481363
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 368724
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477317
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 235295
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 322782
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 459362
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 474761
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 358191
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463236
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 237126
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 281123
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 451706
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 465150
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 351864
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452265
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 228523
              },
              {
                "name": "batch-a-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 369535
              },
              {
                "name": "batch-a-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/batch-a-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 138190
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 283933
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441905
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 425944
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 333518
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 438217
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 213045
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 273001
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 446920
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 410431
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 332108
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 427188
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 204141
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 292614
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 486595
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 428635
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 363803
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455931
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 219832
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 276317
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 434828
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 422507
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 327214
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 420625
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 207528
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 303518
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 429094
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 433113
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 337410
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 436903
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 225364
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309738
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 420272
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 419106
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 328165
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 424304
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 220375
              },
              {
                "name": "01_blender_assembled_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/01_blender_assembled_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1737790
              },
              {
                "name": "02_blender_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/02_blender_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1683905
              },
              {
                "name": "03_blender_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/03_blender_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1749693
              },
              {
                "name": "04_blender_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/04_blender_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1776356
              },
              {
                "name": "05_blender_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/05_blender_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1765618
              },
              {
                "name": "06_blender_exploded_transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/06_blender_exploded_transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1301892
              },
              {
                "name": "blender-assembled-hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1418130
              },
              {
                "name": "blender-exploded-transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview/blender-exploded-transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 938675
              },
              {
                "name": "acrylic-case-exploded-chroma.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-chroma.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1642817
              },
              {
                "name": "acrylic-case-exploded-transparent-v2.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent-v2.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1108713
              },
              {
                "name": "acrylic-case-exploded-transparent.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 401957
              },
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1111809
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 242768
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 325394
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455004
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 484288
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 345973
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460758
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 240094
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 289014
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 472785
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456879
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 353049
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 453756
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214395
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 334942
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 519772
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 477169
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 401168
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 508637
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 245049
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 311410
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476552
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476737
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 363812
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 472449
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232142
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 305529
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441578
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460755
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 346379
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452695
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 227603
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 258138
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 430756
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 452287
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 334113
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441528
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 214068
              },
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 947449
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 245958
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 326989
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 458186
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 486747
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 348667
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 461947
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 242068
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 291238
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 475682
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 458581
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 355847
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 455236
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 216269
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 340339
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 526387
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 481165
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 405389
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 511654
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 248857
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 315351
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 480848
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 479544
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 367077
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 474951
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 234378
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 311688
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 448731
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 466712
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 351991
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456607
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 231875
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 263064
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437124
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 456283
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 338639
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 443471
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserBadgePreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 217843
              },
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 902510
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 187244
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 314462
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441608
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 476483
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 335228
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 449897
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232652
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 277089
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460100
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 447848
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 342061
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 443692
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 207754
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 316647
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 501478
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 460646
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 384323
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 493112
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232722
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 299412
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 463682
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 465566
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 353789
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 464920
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 223590
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 284303
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 419067
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 445569
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 327631
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437531
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 212105
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 297045
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 413887
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 437016
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 320151
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 426779
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLaserIdentificationPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 203550
              },
              {
                "name": "01_soft-neutral_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 414952
              },
              {
                "name": "01_soft-neutral_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 163613
              },
              {
                "name": "01_soft-neutral_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/01_soft-neutral_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 323715
              },
              {
                "name": "02_rose-studio_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 407475
              },
              {
                "name": "02_rose-studio_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 198916
              },
              {
                "name": "02_rose-studio_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/02_rose-studio_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 316039
              },
              {
                "name": "03_amber-gallery_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 387448
              },
              {
                "name": "03_amber-gallery_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 184485
              },
              {
                "name": "03_amber-gallery_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/03_amber-gallery_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 309820
              },
              {
                "name": "04_cool-mist_left.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_left.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 394522
              },
              {
                "name": "04_cool-mist_phone.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_phone.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 189771
              },
              {
                "name": "04_cool-mist_right.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/04_cool-mist_right.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 312810
              },
              {
                "name": "display-case-lighting-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview/display-case-lighting-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 359748
              },
              {
                "name": "all-products-angle-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-angle-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-angle-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-angle-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1132849
              },
              {
                "name": "all-products-phone-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-phone-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-phone-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/all-products-phone-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 245201
              },
              {
                "name": "collector-slab-all-products-hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              },
              {
                "name": "collector-slab-all-products-shipping-final.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-shipping-final.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-shipping-final.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-all-products-shipping-final.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              },
              {
                "name": "collector-slab-material-focus.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-focus.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-focus.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-focus.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 584439
              },
              {
                "name": "collector-slab-material-shipping-final.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-shipping-final.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-shipping-final.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/collector-slab-material-shipping-final.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 584439
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1739788
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1686280
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1541443
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1550003
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1619504
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/gold-four-wing/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1113489
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1722872
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1679004
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1502647
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1549687
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1603442
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/graphite-two-lobe/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1102621
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1684331
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1684598
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1481520
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1520268
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1580862
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-fan-card/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1077251
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1696832
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1650971
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1498775
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1510592
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1563251
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/magnetic-slide-tile/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1086895
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1794376
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1719170
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1565312
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1587224
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1654004
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/metal-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1146378
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1796022
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1711794
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1559235
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1595732
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1661905
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/pointed-three-blade/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 1145610
              },
              {
                "name": "display-case-native-controls-ready.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls-ready.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls-ready.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls-ready.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 648971
              },
              {
                "name": "display-case-native-controls.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 887975
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 389205
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 561452
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441090
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 406112
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 497623
              },
              {
                "name": "06_closed_box.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/06_closed_box.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/06_closed_box.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/06_closed_box.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 270108
              },
              {
                "name": "07_mid_reveal.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/07_mid_reveal.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/07_mid_reveal.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/07_mid_reveal.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 566741
              },
              {
                "name": "08_rounded_square_preset.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/08_rounded_square_preset.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/08_rounded_square_preset.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/08_rounded_square_preset.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 604229
              },
              {
                "name": "09_interactive_half_exploded.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/09_interactive_half_exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/09_interactive_half_exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/09_interactive_half_exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 403615
              },
              {
                "name": "10_interactive_exploded.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/10_interactive_exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/10_interactive_exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/10_interactive_exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 281079
              },
              {
                "name": "11_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/11_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/11_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/11_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 286188
              },
              {
                "name": "display-case-approval-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-approval-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-approval-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-approval-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 493297
              },
              {
                "name": "display-case-reveal-contact-sheet.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-reveal-contact-sheet.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-reveal-contact-sheet.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCasePreview/display-case-reveal-contact-sheet.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 241648
              },
              {
                "name": "01_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/01_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/01_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/01_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 282908
              },
              {
                "name": "02_top.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/02_top.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/02_top.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/02_top.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 442603
              },
              {
                "name": "03_left_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/03_left_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/03_left_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/03_left_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 430277
              },
              {
                "name": "04_right_oblique.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/04_right_oblique.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/04_right_oblique.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/04_right_oblique.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 340153
              },
              {
                "name": "05_low_angle.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/05_low_angle.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/05_low_angle.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/05_low_angle.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 441239
              },
              {
                "name": "06_phone_hero.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/06_phone_hero.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/06_phone_hero.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/06_phone_hero.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 212924
              },
              {
                "name": "07_exploded.png",
                "path": "unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/07_exploded.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/07_exploded.png",
                "url": "../../unity/FidgetingApp/Artifacts/PremiumDisplayCaseThreeBladePreview/07_exploded.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 348867
              }
            ]
          },
          {
            "label": "设计圣经批准证据",
            "folders": [
              "unity/FidgetingApp/Docs/DesignBibleAssets"
            ],
            "explicitFiles": [],
            "note": "六产品、三款材质和推牌展示盒批准图。",
            "state": "approved",
            "files": [
              {
                "name": "collector-slab-materials-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-materials-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 584439
              },
              {
                "name": "collector-slab-six-products-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 548068
              },
              {
                "name": "premium-display-case-slider-approved.png",
                "path": "unity/FidgetingApp/Docs/DesignBibleAssets/premium-display-case-slider-approved.png",
                "absolutePath": "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Docs/DesignBibleAssets/premium-display-case-slider-approved.png",
                "url": "../../unity/FidgetingApp/Docs/DesignBibleAssets/premium-display-case-slider-approved.png",
                "kind": "image",
                "extension": "PNG",
                "sizeBytes": 232142
              }
            ]
          }
        ]
      }
    }
  ]
};
