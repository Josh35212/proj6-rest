<!DOCTYPE html>
<html>
    <head>
        <title>CS322 Project 6</title>
    </head>
    <body>
        <h1>Brevet Times Viewer</h1>
        <form method="GET">
            <select name="endpoint">
                <option value="listAll">All Controls</option>
                <option value="listOpenOnly">Open Times</option>
                <option value="listCloseOnly">Close Times</option>
            </select>
            <select name="format">
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
            </select>
            <input type="number" name="top" min="1" placeholder="Top K">
            <button type="submit">Get Times</button>
        </form>
        <h2>Result</h2>
        <?php
        if (isset($_GET['endpoint'])) {
            $endpoint = $_GET['endpoint'];
            $format = $_GET['format'];
            $top = $_GET['top'];
            $url = "http://api-service:5000/$endpoint/$format";
            
            if ($top && $endpoint != "listAll") {
                $url .= "?top=$top";
            }

            $data = file_get_contents($url);
            
            // Decoding data to look pretty

            if ($format == "json") {
                echo "<pre>";
                // Unescaped slashes fixes MM/DD from looking like MM\/DD
                echo json_encode(json_decode($data), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
                echo "</pre>";
            }
            else {
                echo "<pre>";
                echo $data;
                echo "</pre>";
            }
        }
        ?>
    </body>
</html>