# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['doaxvv_auto_0_8_2.py'],
             pathex=['D:\\Program Files\\Python39\\Lib\\site-packages'],
             binaries=[],
             datas=[('D:\Program Files\Python39\Lib\site-packages\onnxruntime\capi\onnxruntime_providers_shared.dll','onnxruntime\\capi'),('D:\Program Files\Python39\Lib\site-packages\ddddocr\common.onnx','ddddocr')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='doaxvv_auto_0_8_2',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
