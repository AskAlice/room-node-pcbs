#!/usr/bin/env bash
# Re-downloads datasheet PDFs and STEP 3D models (binary assets are not in git).
set -e
cd "$(dirname "$0")/.."
D=docs/datasheets; M=models; mkdir -p $D $M
UA="Mozilla/5.0"
get(){ curl -sL --max-time 90 -A "$UA" -o "$2" "$1"; }
get "https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf" $D/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
get "https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf" $D/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf
get "https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf" $D/esp32-c3-mini-1_datasheet_en.pdf
get "https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf" $D/esp32-c3_datasheet_en.pdf
get "http://www.advanced-monolithic.com/pdf/ds1117.pdf" $D/ds1117.pdf
get "https://www.st.com/resource/en/datasheet/usblc6-2.pdf" $D/usblc6-2.pdf
get "https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf" $D/WS2812B.pdf
get "https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf" $D/4960_SK6812MINI-E_REV02_EN.pdf
get "https://cdn.sparkfun.com/datasheets/Components/General%20IC/ALS-PT19-315C-L177-TR_datasheet.pdf" $D/ALS-PT19-315C-L177-TR_datasheet.pdf
get "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf" $D/bst-bme280-ds002.pdf
get "https://files.seeedstudio.com/wiki/Grove-CO2&Temperature&HumiditySensor-SCD4/res/Sensirion_CO2_Sensors_SCD4x_Datasheet.pdf" $D/SCD4x_datasheet.pdf
get "https://sensirion.com/media/documents/296373BB/6203C5DF/Sensirion_Gas_Sensors_Datasheet_SGP40.pdf" $D/SGP40_datasheet.pdf
get "https://www.aqmd.gov/docs/default-source/aq-spec/resources-page/plantower-pms5003-manual_v2-3.pdf" $D/plantower-pms5003-manual_v2-3.pdf
get "https://files.seeedstudio.com/wiki/Grove-CO2&Temperature&HumiditySensor-SCD4/res/Sensirion_CO2_Sensors_SCD4x_STEP_file.step" $M/Sensirion_SCD4x.step
# Espressif module STEP models: download PCM addon zip and extract 3dmodels/
curl -sL --max-time 180 -o /tmp/esp-addon.zip "https://github.com/espressif/kicad-libraries/releases/latest/download/espressif-kicad-addon.zip"
python3 - <<'PY'
import zipfile,os
z=zipfile.ZipFile('/tmp/esp-addon.zip')
for n in z.namelist():
    if n.endswith('.STEP') and any(k in n for k in ['S3-WROOM-1','C6-WROOM-1','C3-MINI-1']):
        open('models/'+os.path.basename(n),'wb').write(z.read(n))
print('models extracted')
PY
echo "done. See docs/datasheets/README.md for link-only datasheets."
