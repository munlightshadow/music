<?php
include 'config.php';

class Scan
{
	function scan_dir($dir){
    	$pieces = explode("/", $dir);
    	if (end($pieces) == '..')
    	{		    		
    		array_pop($pieces);
    		$dir = str_replace(end($pieces) . '/..', '', $dir);
    		$dir = rtrim($dir, '/');
    	}	

		$conf = new Conf();
		$files = array();
		$files['cur_dir'] = $dir;
        $files['folders'][] = array(
            "name" => '..',
            "path" => $dir . '/..',
            "playlist" => 'false',
            // "items" => scan($dir . '/' . $f) // Recursively get the contents of the folder
        );

		if(file_exists($dir)){
		    foreach(scandir($dir) as $f) {	    	
		        if(!$f || $f[0] == '.') {
		            continue; // Ignore hidden files
		        }
		        if(is_dir($dir . '/' . $f)) {
		            // The path is a folder
		            $option = array();
		            if (file_exists($dir . '/' . $f . '/' . 'conf.json'))
		            {
		            	$option = json_decode(file_get_contents($dir . '/' . $f . '/' . 'conf.json'), true);
		            }
		            $option["name"] = $f;
		            $option["path"] = $dir . '/' . $f;


		            $files['folders'][] = $option;
		        }
		        else {
		        	$pieces = explode(".", $f);
		        	if (in_array(end($pieces), $conf->base_format))
		        	{
			            // It is a file
			            $files['files'][] = array(
			                "name" => $f,
			                "path" => $dir . '/' . $f,
			                "size" => filesize($dir . '/' . $f) // Gets the size of this file
			            );
		        	}
		        }
		    }
		}

		return $files;
	}

	public function get_folder_music($dir){
		$conf = new Conf();
		$files = array();

		if(file_exists($dir)){
		    foreach(scandir($dir) as $f) {	    	
		        if(!$f || $f[0] == '.') {
		            continue; // Ignore hidden files
		        }
		        if(is_dir($dir . '/' . $f)) {
	                $cur_folder_files = $this->get_folder_music($dir . '/' . $f); // Recursively get the contents of the folder
	                foreach ($cur_folder_files as $key => $value) {
	                	$files[] = $value;
	                }
		        }
		        else {
		        	$pieces = explode(".", $f);
		        	if (in_array(end($pieces), $conf->base_format))
		        	{
			            // It is a file
			            $files[] = array(
			                "name" => $f,
			                "path" => $dir . '/' . $f,
			                "size" => filesize($dir . '/' . $f) // Gets the size of this file
			            );
		        	}
		        }
		    }
		}

		return $files;
	}	
}