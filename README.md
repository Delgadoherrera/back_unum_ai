# INSTALL DEPENDENCIES

1- pip -r install ./requirements.txt

## CONFIG PROJECT

2- export GOOGLE_APPLICATION_CREDENTIALS="/home/southatoms/Escritorio/desarrollo/LPA/unum_ia/the-byway-410420-9ab864cb800b.json"
3- export FLASK_APP=__init__:app

## DEPLOY GUNICORN

4-gunicorn -w 4 -b 127.0.0.1:5000 --timeout 60 manage:app

## DIST BASE (Sobreescribira el manage.spec)

1a- pyinstaller manage.py --hidden-import=tiktoken_ext.openai_public -- hidden-import=tiktoken_ext

## manage.spec CONFIGURATION (Incluir carpeta con ruta especifica)

a = Analysis(
    ['manage.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('/home/southatoms/Desktop/developLinux/unum_ia/.env.prod', '.'), 
    ('/home/southatoms/Desktop/developLinux/unum_ia/.env.dev', '.'),
    ('/home/southatoms/Desktop/developLinux/unum_ia/midi_env/lib/python3.10/site-packages/langchain/chains/llm_summarization_checker/prompts', 'langchain/chains/llm_summarization_checker/prompts')
],  
  hiddenimports=['tiktoken_ext.openai_public', 'tiktoken_ext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='manage',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='manage',
)

## DIST ENTREGABLE

pyinstaller manage.spec

## CAmaras de comercio

>Se provee un set de preguntas compuestos por: Código de Pregunta, texto de la pregunta y el formato esperado para el resultado. La respuesta a devolver debe ser en formato json similar a: ["codigo Pregunta" : "Respuesta"] Las respuestas deben ajustar estrictamente a lo preguntado evitando agregados no representativo de las respuesta. En caso de no encontrar una respuesta adecuada para una pregunta la respuesta debe ser un null. La respuesta debe ser en español. El requerimiento tiene las siguientes preguntas: P1 = cual es el nombre del representante del gerente de la empresa. Gerente o representante legal es indistinto uno u otro., el resultado debe ser Texto Libre; P2 = Cuando vence este certificado?, el resultado debe ser Fecha formato dd/mm/aaaa; P3 = Cual es el tipo de identificación del gerente o representante legal?, el resultado debe ser Letras, eliminar . o - o_; P4 = Cual es el número de identificación del gerente o representante legal?, el resultado debe ser un número entero; P5 = Hasta cuanto puede endeudar el representante legal a la sociedad. Si el valor está expresado en salarios mínimos considerar que un salario mínimo equivale a un millón de pesos, el resultado debe ser un valor numérico sin separadores, solo con punto decimal si corresponde; P6 = Cuales son los suplentes del representante legal. Responder con un json que contenga, tipo de identificacion, identificación y nombre. El formato del json debe ser similar a: {"suplentes": ["nombre";"nombre", "tipoId":"tipo de identificacion", "id":"identificacion"]}, el resultado debe ser Texto Libre; P7 = Fecha y hora de expedición del certificado?, el resultado debe ser Fecha en formato dd/mm/aa HH:MM;

## Facturas

>Se provee un set de preguntas compuestos por: Código de Pregunta,  texto de la pregunta y el formato esperado para el resultado. La respuesta a devolver debe ser en formato json similar a:["codigo Pregunta" : "Respuesta"]Las respuestas deben ajustar estrictamente a lo preguntado evitando agregados no representativo de las respuesta. En caso de no encontrar una respuesta adecuada para una pregunta la respuesta debe ser un null. La respuesta debe ser en español.El requerimiento tiene las siguientes preguntas:P1 = Pais donde se emitió la factura, el resultado debe ser Texto Libre;P2..1 = Cual es el  RUC o NIT o RUT o CUIT de la empresa que realiza la factura. No confundir con el RUT,RUC,NIT,CUIT de la imprenta, el resultado debe ser Numérico sin separadores. No tomar lo que se encuentre a la derecha de un guión. Solo Números.;P2..2 = Cual es el número de NIT del receptor de la factura., el resultado debe ser Numérico sin separadores. No tomar lo que se encuentre a la derecha de un guión. Solo Números.;P3 = Fecha de emisión de la factura, el resultado debe ser Fecha formato dd/mm/aaaa;P4 = Número de factura, el resultado debe ser Texto Libre;P5 = Valor total de la factura, el resultado debe ser un valor numérico sin separadores, solo con punto decimal si corresponde;P6 = Valor del IVA , el resultado debe ser un valor numérico sin separadores, solo con punto decimal si corresponde;P7 = Detalle de los items facturados, incluyendo: item (número linea del detalle), código del item , Descripción   , cantidad del ítem numero solo con punto decimal y precio o valor unitario numero solo con punto decimal, sin separadores y precio o valor Total como numero  con punto decimal, si separadores.Algunos de estos datas podrían no figurar en la factura. En ese caso, responder con null, el resultado debe ser Json;

## CONTRATOS

>Se provee un set de preguntas compuestos por: Código de Pregunta, texto de la pregunta y el formato esperado para el resultado. La respuesta a devolver debe ser en formato json similar a: ["codigo Pregunta" : "Respuesta"] Las respuestas deben ajustar estrictamente a lo preguntado evitando agregados no representativo de las respuesta. En caso de no encontrar una respuesta adecuada para una pregunta la respuesta debe ser un null. La respuesta debe ser en español. El requerimiento tiene las siguientes preguntas: P1 = Nombre del contratante o empresa , el resultado debe ser Texto Libre; P2 = Tipo de identificación del contratante o empresa, el resultado debe ser Texto Libre; p3 = Número de identificación del contratante., el resultado debe ser Numérico sin separadores. No tomar lo que se encuentre a la derecha de un guión. Solo Números.; P4 = Nombre del Contratista, el resultado debe ser Texto Libre; P6 = Cual es el objeto del contrato, el resultado debe ser Texto Libre; P7 = Cual es el valor del contrato que está expresado en letras sin considerar decimales., el resultado debe ser un valor numérico sin separadores, solo con punto decimal si corresponde; P8 = Detalle de las pólizas y/o garantías solicitadas en formato json similar a: [{"Póliza":"descripción de poliza", "Porcentaje":"porcentaje"} ], el resultado debe ser Json;

## Comprobantes de pagos y transferencias

>Contestar solo rcon la espuesta, no repetir la pregunta hecha en el contenido de la respuesta:Se provee un set de preguntas compuestos por: Código de Pregunta,  texto de la pregunta y el formato esperado para el resultado. La respuesta a devolver debe ser en formato json y  siempre debe contener a) El código de pregunta c) la respuesta; Las respuestas deben ajustar estrictamente a lo preguntado evitando agregados no representativo de las respuesta. En caso de no encontrar una respuesta adecuada para una pregunta la respuesta debe ser un null. La respuesta debe ser en español.El requerimiento tiene las siguientes preguntas:CBU = Cual es la CBU o cuenta  destino de la empresa que realiza el pago o transferencia en caso que se indiquen ambas optar por CBU. Debe ser un número de 22 dígitos?, el resultado debe ser Solo los números sin separadores;cuentaOrigen = Cual es la cuenta origen o débito ?, el resultado debe ser Solo los números sin separadores.;CUIT = Cual es el CUIT CUIL o CDI del destinatario o beneficiario, es un número de 11 dígitos?, el resultado debe ser Texto Libre; FechaPago = Cual es la fecha y hora de la transacción en formato dd/mm/aaaa hh:mm?, el resultado debe ser Fecha en formato dd/mm/aa HH:MM; nroTransaccion = Cual es el número de transacción u operación?, el resultado debe ser Solo los números sin separadores;ValorPago = Cual es el valor del pago o de la transferencia?, el resultado debe ser un valor numérico sin separadores, solo con punto decimal si corresponde;
