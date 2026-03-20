<?php
/**
 * Check updates for local CSS files
 */

// Silenciamos errores para que no rompan el JSON de salida
error_reporting(0);
ini_set('display_errors', 0);

header('Content-Type: application/json');

$urls = [
    '../css/bootstrap.min.css' => 'https://www.argentina.gob.ar/profiles/argentinagobar/themes/contrib/poncho/vendor/bootstrap/css/bootstrap.min.css',
    '../css/icono-arg.css' => 'https://www.argentina.gob.ar/profiles/argentinagobar/themes/contrib/poncho/css/icono-arg.css',
    '../css/poncho.min.css' => 'https://www.argentina.gob.ar/profiles/argentinagobar/themes/contrib/poncho/css/poncho.min.css'
];

$up_to_date = true;
$last_modified_date = "";

// Verificamos si cURL está disponible
if (!function_exists('curl_init')) {
    echo json_encode([
        'up_to_date' => true,
        'last_modified' => 'Deshabilitado',
        'error' => 'cURL no está instalado en el servidor'
    ]);
    exit;
}

foreach ($urls as $local_file => $remote_url) {
    if (!file_exists($local_file)) {
        $up_to_date = false;
        continue;
    }

    $ch = curl_init($remote_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36");
    curl_setopt($ch, CURLOPT_ENCODING, "");
    curl_setopt($ch, CURLOPT_TIMEOUT, 5); // Timeout para no bloquear el hilo

    $response = curl_exec($ch);
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($response === false || $http_code !== 200) {
        // Si falla el remoto por red, no marcamos como 'outdated' necesariamente, 
        // pero podrías decidir lo contrario. Aquí asumimos que si no podemos conectar, no sabemos.
        continue;
    }

    $header = substr($response, 0, $header_size);
    $body = substr($response, $header_size);

    if (preg_match('/[Ll]ast-[Mm]odified:\s*(.*?)\r\n/i', $header, $matches)) {
        $remote_date_str = $matches[1];
        $time = strtotime($remote_date_str);
        if ($time && empty($last_modified_date)) {
            $last_modified_date = date("d/m/Y H:i", $time);
        }
    }

    $remote_md5 = md5($body);
    $local_md5 = md5_file($local_file);

    if ($remote_md5 !== $local_md5) {
        $up_to_date = false;
    }
}

if (empty($last_modified_date)) {
    $last_modified_date = "Reciente";
}

echo json_encode([
    'up_to_date' => $up_to_date,
    'last_modified' => $last_modified_date
]);