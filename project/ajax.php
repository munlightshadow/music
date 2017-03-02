<?php
include 'scan.php';

$conf = new Conf();
$scan = new Scan();

// $base_dir = "/mnt/main/Music";
$base_dir = $conf->base_dir;

if (isset($_POST['type']) && $_POST['type'] == 'get_tree')
{
	if (isset($_POST['base_dir']) && $_POST['base_dir'] != '') {$dir = $_POST['base_dir'];} else {$dir = $base_dir;}
	// Run the recursive function 
	$response = $scan->scan_dir($dir);	
}

if (isset($_POST['type']) && $_POST['type'] == 'get_folder_music')
{
	if (isset($_POST['base_dir']) && $_POST['base_dir'] != '') {$dir = $_POST['base_dir'];} else {$dir = $base_dir;}
	// Run the recursive function 
	$response = $scan->get_folder_music($dir);	
}


echo json_encode($response);