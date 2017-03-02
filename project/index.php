<!ELEMENT audio EMPTY >
<!ATTLIST audio 
src CDATA #REQUIRED
preload (auto, yes, no) auto
>
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Music</title>

        <script type="text/javascript" src="plugin/jquery/1.10.2/jquery-1.10.2.min.js" ></script>
        
        <!-- audio -->
        <script type="text/javascript" src="plugin/jplayer/jquery.jplayer/jquery.jplayer.js"></script>
        <script type="text/javascript" src="plugin/jplayer/add-on/jplayer.playlist.js"></script>
        <!-- <link href="plugin/jplayer/lib/jPlayer.2.6.0/skin/vkontakte/vkontakte.css" rel="stylesheet" type="text/css" /> -->
        <link href="plugin/jplayer/skin/blue.monday/jplayer.blue.monday.css" rel="stylesheet" type="text/css" />        

        <link href="style.css" rel="stylesheet">
    </head> 
    <body>
        <header>
            <h1 id="header_text">111</h1>
        </header>

        <div id="content_left">
            <div class="label">folders</div>
            <!-- <div class="clear"></div> -->
            <div id="folders"></div>
            <!-- <div class="clear"></div> -->
            <div class="label">files</div>
            <!-- <div class="clear"></div>         -->
            <div id="files"></div>
            <!-- <div class="clear"></div>         -->
        </div>
        

        <div id="content_right">

        <div class="clear_playlist">Clear All</div>

            <div id="jquery_jplayer_1" class="jp-jplayer"></div>
            <div id="jp_container_1" class="jp-audio">

                <div class="jp-type-playlist">
                    <div class="jp-gui jp-interface">
                        <ul class="jp-controls">
                            <li>
                                <label id="name-of-the-song-that-plays"></label>
                            </li>
                            <li><a href="javascript:;" class="jp-play" tabindex="1">play</a></li>
                            <li><a href="javascript:;" class="jp-pause" tabindex="1">pause</a></li>
                            <li><a href="javascript:;" class="jp-previous" tabindex="1">previous</a></li>
                            <li><a href="javascript:;" class="jp-next" tabindex="1">next</a></li>
                            <div class="clear"></div>
                        </ul>
                        <!-- Прогресс бар -->
                        <div class="jp-progress">
                            <div class="jp-seek-bar">
                                <div class="jp-play-bar"></div>
                            </div>
                        </div>
                        <!-- Регулятор громкости -->
                        <div class="jp-volume-bar">
                            <div class="jp-volume-bar-value"></div>
                        </div>
                        <!-- Остаток времени -->
                        <div class="jp-time-holder">
                            <div class="jp-current-time"></div>
                        </div>

                        <div class="clear"></div>

                        <!-- Кнопки повторения и перемешивания плейлиста -->
                        <ul class="jp-toggles">
                            <li>
                                <a href="javascript:;" class="jp-shuffle" tabindex="1" title="shuffle">shuffle</a>
                            </li>
                            <li>
                                <a href="javascript:;" class="jp-shuffle-off" tabindex="1" title="shuffle off">shuffle off</a>
                            </li>
                            <li>
                                <a href="javascript:;" class="jp-repeat" tabindex="1" title="repeat">repeat</a>
                            </li>
                            <li>
                                <a href="javascript:;" class="jp-repeat-off" tabindex="1" title="repeat off">repeat off</a>
                            </li>
                        </ul>
                        <div class="clear"></div>
                    </div>
                    <!-- Будущий плейлист -->
                    <div class="jp-playlist">
                        <ul>
                            <li></li>
                        </ul>
                    </div>
                    <!-- Сообщение об ошибке -->
                    <div class="jp-no-solution">
                        <span>Update Required</span>
                        To play the media you will need to either update your browser to a recent version or update your 
                        <a href="http://get.adobe.com/flashplayer/" target="_blank">
                            Flash plugin
                        </a>.
                    </div>
                </div>
            </div>

        </div>

        <div class="clear"></div>       

        <footer>
            <!-- Copyright -->
        </footer>
    </body> 
</html>

<script>
    var myPlaylist;
    var step = 0;

    function send_ajax_get_folder_tree(dir){

        $.ajax({
            url: 'ajax.php',
            dataType: 'json',
            method: 'post',
            data: {base_dir : dir, type : 'get_tree'},
            success: function(data){
                var html = '';
                if (data.folders != undefined)
                {
                    var first_folder = true;
                    data.folders.forEach(function(item, i, arr) {
                        var attr_back = '';
                        var add_class = '';
                        if (step != 0 || !first_folder)
                        {                            
                            if (step != 0 && first_folder) {attr_back = 'id="back_folder" '; add_class = 'directory-up ';}
                            if (item.playlist == 'false') {var div_add_dir = '';} else {var div_add_dir = '<div class="add_folder">+</div>';}
                            if (item.folder_art == undefined) {
                                var background_art = '';
                            } else {
                                var path_to_background_img = item.path + '/' + item.folder_art;
                                path_to_background_img = path_to_background_img.replace(/\s/ig, '%20');
                                var background_art = 'background-image: url(' + path_to_background_img + ')';
                            }                            
                            if (item.display == undefined || item.display != 'none') {
                                html += '<div class="wrapper_folder"><div ' + attr_back + ' style="' + background_art + '" class="' + add_class + 'folder" attr-path="' + item.path + '">' + '</div>' + div_add_dir + '<div class="folder_name">' + item.name + '</div></div>';
                            }
                        }
                        first_folder = false;
                    });                    
                }
                $("#folders").html(html);
                
                html = '';
                if (data.files != undefined)                
                {
                    data.files.forEach(function(item, i, arr) {
                        html += '<div class="file" attr-path="' + item.path + '">' + item.name + '</div><div class="add_file">+</div>';
                    });                
                }
                $("#header_text").html(data.cur_dir);
                $("#files").html(html);
            },
            error: function(){
                alert('error');
            }
        });        

    }
 
    function send_ajax_get_folder_music(dir){

        $.ajax({
            url: 'ajax.php',
            dataType: 'json',
            method: 'post',
            data: {base_dir : dir, type : 'get_folder_music'},
            success: function(data){
                data.forEach(function(i,elem) {
                    myPlaylist.add({
                        author:"unknow",
                        discription: i.path,
                        title: i.name + '<br>' + i.path,
                        mp3: i.path
                    })
                });  

            },
            error: function(){
                alert('error');
            }
        });        

    }



    $(document).ready(function(){
        send_ajax_get_folder_tree('');


$('#jquery_jplayer_1').jPlayer({
 swfPath: 'plugin/jplayer/jquery.jplayer',
 solution: 'html, flash',
 supplied: 'm4a, oga, mp3',
 preload: 'metadata',
 volume: 0.8,
 muted: false,
 backgroundColor: '#000000',
 cssSelectorAncestor: '#jp_container_1',
 cssSelector: {
  videoPlay: '.jp-video-play',
  play: '.jp-play',
  pause: '.jp-pause',
  stop: '.jp-stop',
  seekBar: '.jp-seek-bar',
  playBar: '.jp-play-bar',
  mute: '.jp-mute',
  unmute: '.jp-unmute',
  volumeBar: '.jp-volume-bar',
  volumeBarValue: '.jp-volume-bar-value',
  volumeMax: '.jp-volume-max',
  playbackRateBar: '.jp-playback-rate-bar',
  playbackRateBarValue: '.jp-playback-rate-bar-value',
  currentTime: '.jp-current-time',
  duration: '.jp-duration',
  title: '.jp-title',
  fullScreen: '.jp-full-screen',
  restoreScreen: '.jp-restore-screen',
  repeat: '.jp-repeat',
  repeatOff: '.jp-repeat-off',
  gui: '.jp-gui',
  noSolution: '.jp-no-solution'
 },
 errorAlerts: false,
 warningAlerts: false
});

        var cssSelector = {
            // jPlayer: "#jquery_jplayer_1", 
            cssSelectorAncestor: "#jp_container_1"
        };

        var playlist = [
        ];

        var options = {
            swfPath: "js",
            // autoPlay: true,
            supplied: "oga, mp3",
            wmode: "window",
            smoothPlayBar: false,
            keyEnabled: true
        };

        myPlaylist = new jPlayerPlaylist(cssSelector, playlist, options);
    });    

    $('body').on('click', '.folder', function(){
        if ($(this).attr('id') == "back_folder") {step--;} else {step++;}
        $("#folders").html('');
        $("#files").html('');        
        send_ajax_get_folder_tree($(this).attr('attr-path'));
    })

    $('body').on('click', '.folder_name', function(){
        $(this).prevAll('.folder:first').click();
    })    

    $('body').on('click', '.add_folder', function(event){
        send_ajax_get_folder_music($(this).prev().attr('attr-path'));
    })   

    $('body').on('click', '.add_file', function(){
            var start_pos = 0;

            myPlaylist.add({
                author:"unknow",
                discription: $(this).prev().attr('attr-path'),
                title: $(this).prev().html() + '<br>' + $(this).prev().attr('attr-path'),
                mp3: $(this).prev().attr('attr-path')
            })

            // myPlaylist.play(start_pos);            
    })   

    $('body').on('click', '.clear_playlist', function(){
        myPlaylist.remove();
    })
</script>