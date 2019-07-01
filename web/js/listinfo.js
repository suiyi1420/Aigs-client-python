var imageNr = 0; // Serial number of current image
    var finished = new Array(); // References to img objects which have finished downloading
    var paused = true;
    var shipinUrl="";
    var device_status = {};
    var socket = null;
    var auto;
    var ip;
    var device_data = {
        temp: 0,
        sunLight: 0,
        humidity: 0,
        watertemp: 0,
        lamp: false,
        food: false,
        food_speed: 0,
        turangshidu: true,
        min_temp: 0,
        max_temp: 0,
        min_humidity: 0,
        max_humidity: 0,
        min_lamp: 0,
        max_lamp: 0,
        device_status: {
            penshui_status: 0, lamp_status: 0, food_status: 0
        }
    }


$(document).ready(function() {
		
        socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
		socket.on("connect", function(evt) {
			$(".bg-connect").hide();
			var msg = {"msg": 'connect'};
			console.log(msg);
			var json = JSON.stringify(msg);
			socket.emit("response",json+"")
		})
		socket.on("my_message", function(evt) {
			alert(evt.data)
		})
        socket.on("response", function(evt) {
            var data = evt;
                try {
                    data = data.replace(/'/g, "\"");
                    console.log(data)
                    data = JSON.parse(data);
                    var msg = data["msg"];
                    var status = data["status"];

                    if(msg=="food_status"){
                        device_status.food_status = parseInt(data.food_status);
                        $("#food").attr("data-status", device_status.food_status);
                        if (device_status.food_status == 0) {
                            $("#food_controller").removeClass("olive").addClass("gray");
                            $("#food_controller .data-state-item-right-text3").text("已关闭");
                        } else {
                            $("#food_controller").removeClass("gray").addClass("olive");
                            $("#food_controller .data-state-item-right-text3").text("已开启");
                        }
                    }
                    if (msg == "get") {

                        auto = data.list["auto"];
                        device_status.lamp_status = parseInt(data.list.status.lamp);

                        device_status.penshui_status = parseInt(data.list.status.penshui);
                        device_status.temp_status = parseInt(data.list.status.temp);
                        device_status.watertemp_status = parseInt(data.list.status.watertemp);
                        var temp = 0, sunLight = 0, humidity = 0, water = 0, lamp = 0, food = 0, turangshidu = 0;
                        if (auto["autoClock"] == 1 || auto["autoClock"]  == "1") {
                            $('input[name="my-checkbox"]').bootstrapSwitch('state', true);
                        } else {
                            $('input[name="my-checkbox"]').bootstrapSwitch('state', false);
                            $("#watertemp,#temp,#lamp,#humidity").removeClass("isAuto");
                        }
                        checkAuto(auto);
                        changeStatus1(auto, device_status);
                        if (data.list.critical.food != null && data.list.critical.food != "") {
                            device_data.food_speed= parseInt(data.list.critical.food.food_speed);
                            device_data.food_running_time= parseInt(data.list.critical.food.food_running_time);
                            device_data.food_chixu= parseInt(data.list.critical.food.food_chixu_time);
                            if(device_data.food_speed=="0"){
                                device_data.food_speed="慢";
                            }else if(device_data.food_speed=="1"){
                                device_data.food_speed="快";
                            }
                            $("#food_speed_text").text(device_data.food_speed);
                            $("#food_chixu_text").text(device_data.food_chixu);
                            var food_running_time=data.list.critical.food.food_running_time;
                            if(food_running_time=="0"){
                                $("#food_nextTime_text").text("无下次喂食时间");
                            }else {
                                $("#food_nextTime_text").text("周" + getWeek(food_running_time.week) + " " + food_running_time.time);
                            }
                        }
                        if (data.list.light != null && data.list.light != "") {//光照
                            device_data.sunLight = parseInt(data.list.light);
                            device_data.min_lamp = parseInt(data.list.critical.lamp.min);
                            device_data.max_lamp = parseInt(data.list.critical.lamp.max);
                            $("#lamp .data-state-item-value").text(device_data.min_lamp + "Lx ~ " + device_data.max_lamp);
                            $("#lamp .data-state-item-right-text").text(device_data.sunLight);
                            if (device_data.sunLight >= device_data.min_lamp) {
                                $("#lamp .data-state-item-right-text3").text("白天");
                                $("#lamp .data-state-item-pic").addClass("fa-sun-o fa-spin").removeClass("fa-moon-o");
                            } else if(device_data.sunLight < device_data.min_lamp){
                                $("#lamp .data-state-item-right-text3").text("黑夜");
                                $("#lamp .data-state-item-pic").addClass("fa-moon-o").removeClass("fa-sun-o fa-spin");
                            }
                        }
                        if (data.list.temp != null && data.list.temp != "") {//空气温度
                            device_data.temp = parseInt(data.list.temp);
                            device_data.min_temp = parseInt(data.list.critical.temp.min);
                            device_data.max_temp = parseInt(data.list.critical.temp.max);
                            $("#temp .data-state-item-value").text(device_data.min_temp + "℃ ~ " + device_data.max_temp + "℃");
                            $("#temp .data-state-item-right-text").text(device_data.temp);
                            if (device_data.temp < device_data.min_temp) {
                                $("#temp .data-state-item-pic").addClass("fa-thermometer-empty cold").removeClass("fa-thermometer-half green2 fa-thermometer-full red");
                                $("#temp .data-state-item-right-pic").addClass("fa-snowflake-o fa-spin cold").removeClass("fa-cloud green2 fa-fire red");
                            } else if (device_data.temp >= device_data.min_temp && device_data.temp <= device_data.max_temp) {
                                $("#temp .data-state-item-pic").removeClass("fa-thermometer-empty cold fa-thermometer-full red").addClass("fa-thermometer-half green2");
                                $("#temp .data-state-item-right-pic").removeClass("fa-snowflake-o fa-spin cold fa-fire red").addClass("fa-cloud green2");
                            } else if (device_data.temp > device_data.max_temp) {
                                $("#temp .data-state-item-pic").removeClass("fa-thermometer-empty cold fa-thermometer-half green2").addClass("fa-thermometer-full red");
                                $("#temp .data-state-item-right-pic").removeClass("fa-snowflake-o fa-spin cold fa-cloud green2").addClass("fa-fire red");
                            }

                        }
                        if (data.list.humidity != null && data.list.humidity != "") {//湿度
                            device_data.humidity = parseInt(data.list.humidity);
                            device_data.min_humidity = parseInt(data.list.critical.humidity.min);
                            device_data.max_humidity = parseInt(data.list.critical.humidity.max);
                            $("#humidity .data-state-item-value").text(device_data.min_humidity + "% ~ " + device_data.max_humidity + "%");
                            $("#humidity .data-state-item-right-text").text(device_data.humidity);
                            if (device_data.humidity < device_data.min_humidity) {
                                $("#humidity .data-state-item-right-text3").text("干燥");
                            } else if (device_data.humidity >= device_data.min_humidity && device_data.humidity <= device_data.max_humidity) {
                                $("#humidity .data-state-item-right-text3").text("舒适");
                            } else if (device_data.humidity > device_data.max_humidity) {
                                $("#humidity .data-state-item-right-text3").text("潮湿");
                            }

                        }
                        if (data.list.watertemp != null && data.list.watertemp != "") {//水温
                            device_data.watertemp = parseInt(data.list.watertemp);
                            device_data.min_watertemp = parseInt(data.list.critical.watertemp.min);
                            device_data.max_watertemp = parseInt(data.list.critical.watertemp.max);
                            $("#watertemp .data-state-item-value").text(device_data.min_watertemp + "℃ ~ " + device_data.max_watertemp + "℃");
                            $("#watertemp .data-state-item-right-text").text(device_data.watertemp);
                            if (device_data.watertemp < device_data.min_watertemp) {
                                $("#watertemp .data-state-item-pic").addClass("fa-thermometer-empty cold").removeClass("fa-thermometer-half green2 fa-thermometer-full red");
                                $("#watertemp .data-state-item-right-pic").addClass("fa-snowflake-o fa-spin cold").removeClass("fa-cloud green2 fa-fire red");
                            } else if (device_data.watertemp >= device_data.min_watertemp && device_data.watertemp <= device_data.max_watertemp) {
                                $("#watertemp .data-state-item-pic").removeClass("fa-thermometer-empty cold fa-thermometer-full red").addClass("fa-thermometer-half green2");
                                $("#watertemp .data-state-item-right-pic").removeClass("fa-snowflake-o fa-spin cold fa-fire red").addClass("fa-cloud green2");
                            } else if (device_data.watertemp > device_data.max_watertemp) {
                                $("#watertemp .data-state-item-pic").removeClass("fa-thermometer-empty cold fa-thermometer-half green2").addClass("fa-thermometer-full red");
                                $("#watertemp .data-state-item-right-pic").removeClass("fa-snowflake-o fa-spin cold fa-cloud green2").addClass("fa-fire red");
                            }

                        }
                        /*if (data.list.turanshidu != null && data.list.turanshidu != "") {
                            if (data.list.turanshidu == "1") {
                                $("#turangshidu .data-state-item-pic").addClass("fa-envira").removeClass("fa-pied-piper");
                                $("#turangshidu .data-state-item-right-text3").text("湿润");
                            } else if (data.list.turanshidu == "0") {
                                $("#turangshidu .data-state-item-pic").addClass("fa-pied-piper").removeClass("fa-envira");
                                $("#turangshidu .data-state-item-right-text3").text("干燥");
                            }
                        }*/


                    } else if (msg == "connect") {
                        
                    }else if(msg=="food_time_list"){//自动喂食时间列表
                        var food_time_list=mergeObject(data["list"]);
                        setFoodHtml(food_time_list)
                    }
                    

                } catch (e) {
                    console.log(e);
                }
        });
 $("[name='my-checkbox']").bootstrapSwitch();
        $("[name='shipin-checkbox']").bootstrapSwitch('state', false);
        //$("[name='wangluo-checkbox']").bootstrapSwitch({'state': true,'onText':'外网','offText':'内网','offColor':'danger'});


        $('input[name="my-checkbox"]').on('switchChange.bootstrapSwitch', function (event, state) {
            console.log(state); // true | false
            var value = state;
            console.log(value);
            var msg;
            if (value) {
                msg = {"msg": 'change', "key": 'autoClock', "value": '1'};
            } else {
                msg = {"msg": 'change', "key": 'autoClock', "value": '0'};
                $("#watertemp,#temp,#lamp,#humidity").removeClass("isAuto");
            }
            var json = JSON.stringify(msg);
            console.log(json);
            if (socket != null) {
                socket.emit("response",json+"");
            }
        });
        $('input[name="shipin-checkbox"]').on('switchChange.bootstrapSwitch', function (event, state) {
            if(state){//打开
                $("#cameraImg").attr("src","");
                camera();

            }else{//关闭
				var msg = {"msg": 'closed'};
				console.log(msg);
				var json = JSON.stringify(msg);
				socket.emit("response",json+"")
                socket.disconnect(true);

                $("#cameraImg").hide();

            }
        });

        $("#temp_text,#lamp_text,#humidity_text,#watertemp_text").click(function(e){
            e.stopPropagation();
            var dtype=$(this).parent().attr("data-device");
            var dname=$(this).parent().attr("data-devicename");
            $("#Modal").attr("device",dtype);
            $("#myModalLabel").text(dname);
            $("#Modal input").val("");
            $("#Modal").modal('toggle');
        });
        $("#food_nextTime_text,#food .data-state-item-right").click(function(e){
            e.stopPropagation();
        });
    });


    function resetCamera(){
        var shipinOpen=$('input[name="shipin-checkbox"]').bootstrapSwitch('state');
        if(shipinOpen){
            $("[name='shipin-checkbox']").bootstrapSwitch('state', false);

        }
        var ttime=30;
        function countDown(){
            if(ttime==0){
                $(".switc-reset").attr("onclick","resetCamera()");
                $(".switc-reset").text("重启摄像头");
                $(".switc-reset").removeClass("disable");
                clearInterval(timer);
            }else{
                $(".switc-reset").addClass("disable");
                $(".switc-reset").removeAttr("onclick");
                $(".switc-reset").text("重启摄像头("+ttime+"s)");
            }
            ttime--;
        }
        var timer=setInterval(countDown,1000);
        var msg = {"msg": 'resetCamera'};
        console.log(msg);
        var json = JSON.stringify(msg);
        if (socket != null) {
            socket.emit("response",json+"");
        }
        alert("设备摄像头正在重启，请等待30秒后再次打开。")
    }
    function tijiaoUrl(){
        shipinUrl="http://"+$("#wangluo_input input").val()+":8080/?action=snapshot&n=" + (++imageNr);

        paused=false;
        createImageLayer();
    }
    function changeMinMax(){
        var device=$("#Modal").attr("device");
        if($("#min").val()==""||$("#max").val()==""){
            alert("请输入数值");
        }else{
            var msg = { "msg": 'set', "type": "device", "device": device, "min": $("#min").val(), "max": $("#max").val() };
            var json = JSON.stringify(msg);
            console.log(json);
            socket.emit("response",json+"");
            $("#Modal").modal('toggle');
        }

    }
    function setWifi(){
        var ssid=$("#ssid").val();
        var password=$("#password").val();
        if(ssid==""||password==""){
            alert("请输入wifi的SSID和密码");
        }else{
            var msg = { "msg": 'setWifi', "ssid": ssid, "password": password };
            var json = JSON.stringify(msg);
            console.log(json);
            socket.emit("response",json+"");
            $("#WIFI").modal('toggle');
            alert("Wifi设置成功，请等待设备重启");
            window.location.href='${path}/index';
        }

    }
    

    //检测每个传感器是否自动监控
    function checkAuto(auto){
        $("#temp").attr("data-isAuto",auto.temp_auto);
        $("#lamp").attr("data-isAuto",auto.lamp_auto);
        $("#humidity").attr("data-isAuto",auto.humidity_auto);
        $("#watertemp").attr("data-isAuto",auto.watertemp_auto);
        $("#food").attr("data-isAuto",auto.food_auto);
        if(auto["autoClock"].toString() == "1"){
            $("#watertemp").attr("onclick","changeAuto(this)");
            $("#temp").attr("onclick","changeAuto(this)");
            $("#lamp").attr("onclick","changeAuto(this)");
            $("#humidity").attr("onclick","changeAuto(this)");
            $("#food").attr("onclick","changeAuto(this)");

            if(auto.temp_auto.toString()=="0"){
                $("#temp").removeClass("isAuto");
                $("#temp_controller").attr("onclick", "changeDevice(this)");
            }else{
                $("#temp").addClass("isAuto");
                $("#temp_controller").removeAttr("onclick");
            }
            if(auto.lamp_auto.toString()=="0"){
                $("#lamp").removeClass("isAuto");
                $("#lamp_controller").attr("onclick", "changeDevice(this)");
            }else{
                $("#lamp").addClass("isAuto");
                $("#lamp_controller").removeAttr("onclick");
            }
            if(auto.humidity_auto.toString()=="0"){
                $("#humidity").removeClass("isAuto");
                $("#humidity_controller").attr("onclick", "changeDevice(this)");
            }else{
                $("#humidity").addClass("isAuto");
                $("#humidity_controller").removeAttr("onclick");
            }
            if(auto.watertemp_auto.toString()=="0"){
                $("#watertemp").removeClass("isAuto");
                $("#watertemp_controller").attr("onclick", "changeDevice(this)");
            }else{
                $("#watertemp").addClass("isAuto");
                $("#watertemp_controller").removeAttr("onclick");
            }
            if(auto.food_auto.toString()=="0"){
                $("#food").removeClass("isAuto");
                $("#food_controller").attr("onclick", "changeDevice(this)");
            }else{
                $("#food").addClass("isAuto");
                $("#food_controller").removeAttr("onclick");
            }
        }else{
            $("#watertemp").attr("onclick","");
            $("#temp").attr("onclick","");
            $("#lamp").attr("onclick","");
            $("#humidity").attr("onclick","");
            $("#food").attr("onclick","");
            $("#lamp_controller").attr("onclick", "changeDevice(this)");
            $("#temp_controller").attr("onclick", "changeDevice(this)");
            $("#humidity_controller").attr("onclick", "changeDevice(this)");
            $("#watertemp_controller").attr("onclick", "changeDevice(this)");
            $("#food_controller").attr("onclick", "changeDevice(this)");
        }

    }

    //修改传感器是否自动监控
    function changeAuto(_this){
        _this=$(_this);
        var device_auto=_this.attr("data-auto");
        var device_isAuto=_this.attr("data-isAuto");
        var msg;
        if (device_isAuto==1||device_isAuto=="1"){
            msg={"msg":"changeAuto","type":device_auto,"status":"0"};
            _this.attr("data-isAuto","0");
            _this.removeClass("isAuto");
        }else{
            msg={"msg":"changeAuto","type":device_auto,"status":"1"};
            _this.attr("data-isAuto","1");
            _this.addClass("isAuto");
        }
        var json = JSON.stringify(msg);
        console.log(json);
        socket.emit("response",json+"");

    }

    function changeStatus1(auto, device_status) {
        $("#lamp_controller").attr("data-status", device_status.lamp_status);

        $("#humidity_controller").attr("data-status", device_status.penshui_status);
        $("#temp_controller").attr("data-status", device_status.temp_status);
        $("#watertemp_controller").attr("data-status", device_status.watertemp_status);
        if (device_status.lamp_status == 0) {
            $("#lamp_controller").removeClass("yellow").addClass("gray");
            $("#lamp_controller .data-state-item-right-text3").text("已关闭");
        } else {
            $("#lamp_controller").removeClass("gray").addClass("yellow");
            $("#lamp_controller .data-state-item-right-text3").text("已开启");
        }

        if (device_status.penshui_status == 0) {
            $("#humidity_controller").removeClass("water").addClass("gray");
            $("#humidity_controller .data-state-item-right-text3").text("已关闭");
        } else {
            $("#humidity_controller").removeClass("gray").addClass("water");
            $("#humidity_controller .data-state-item-right-text3").text("已开启");
        }
        if (device_status.watertemp_status == 0) {
            $("#watertemp_controller .data-state-item-right-text3").text("已关闭");
            $("#watertemp_controller .reshui ").removeClass("active");
            $("#watertemp_controller").removeClass("orange").addClass("gray");
        } else {
            $("#watertemp_controller").removeClass("gray").addClass("orange");
            $("#watertemp_controller .reshui ").addClass("active");
            $("#watertemp_controller .data-state-item-right-text3").text("已开启");
        }
        if (device_status.temp_status == 0) {
            $("#temp_controller").removeClass("red").addClass("gray");
            $("#temp_controller .jiawen ").removeClass("active");
            $("#temp_controller .data-state-item-right-text3").text("已关闭");
        } else {
            $("#temp_controller").removeClass("gray").addClass("red");
            $("#temp_controller .jiawen ").addClass("active");
            $("#temp_controller .data-state-item-right-text3").text("已开启");
        }
    }

    function changeDevice(_this) {
        //var device_status = $(_this).attr("device_status");
        var typ = $(_this).attr("data-type");
        var stat = $(_this).attr("data-status");
        var statusType = $(_this).attr("data-statustype");
        var msg;
        if (stat == 1 || stat == "1") {
            msg = {"msg": 'changeDevice', type: typ, status: '0'};
            device_status[statusType] = "0";
            if(statusType=="lamp_status"){
                $("#lamp_controller").removeClass("yellow").addClass("gray");
                $("#lamp_controller .data-state-item-right-text3").text("已关闭");

            }else if(statusType=="penshui_status"){
                $("#humidity_controller").removeClass("water").addClass("gray");
                $("#humidity_controller .data-state-item-right-text3").text("已关闭");
            }else if(statusType=="watertemp_status"){
                $("#watertemp_controller .data-state-item-right-text3").text("已关闭");
                $("#watertemp_controller .reshui ").removeClass("active");
                $("#watertemp_controller").removeClass("orange").addClass("gray");
            }else if(statusType=="temp_status"){
                $("#temp_controller").removeClass("red").addClass("gray");
                $("#temp_controller .jiawen ").removeClass("active");
                $("#temp_controller .data-state-item-right-text3").text("已关闭");
            }

        } else {
            msg = {"msg": 'changeDevice', type: typ, status: '1'};
            device_status[statusType] = "1";

            if(statusType=="lamp_status"){
                $("#lamp_controller").removeClass("gray").addClass("yellow");
                $("#lamp_controller .data-state-item-right-text3").text("已开启");
            }else if(statusType=="penshui_status"){
                $("#humidity_controller").removeClass("gray").addClass("water");
                $("#humidity_controller .data-state-item-right-text3").text("已开启");
            }else if(statusType=="watertemp_status"){
                $("#watertemp_controller").removeClass("gray").addClass("orange");
                $("#watertemp_controller .reshui ").addClass("active");
                $("#watertemp_controller .data-state-item-right-text3").text("已开启");
            }else if(statusType=="temp_status"){
                $("#temp_controller").removeClass("gray").addClass("red");
                $("#temp_controller .jiawen ").addClass("active");
                $("#temp_controller .data-state-item-right-text3").text("已开启");
            }else if(statusType=="food_status"){
                $("#food_controller").removeClass("gray").addClass("olive");
                $("#food_controller .data-state-item-right-text3").text("已开启");
				setTimeout(function(){
					$("#food_controller").removeClass("olive").addClass("gray");
                    $("#food_controller .data-state-item-right-text3").text("已关闭");
					device_data.food_status=0
				},parseInt(device_data.food_chixu*1000))
            }
        }

        //_this.setData({ device_status: device_status })
        var json = JSON.stringify(msg);
        console.log(json);
        socket.emit("response",json+"");

    }


    function camera(){
        socket = io.connect('http://${ip}:9000?poster=${userId}&type=1&receiver=${device_num}',params={'poster': '${userId}','type':'1','receiver':'${device_num}'});
        socket.on('connect', function(){
            socket.emit("response", "open")
            //alert("视频连接成功！");
            $("#cameraImg").show();
        });
        socket.on('close', function(data){
            alert("设备摄像服务已关闭！")
            socket.disconnect(true);
            $("#cameraImg").hide();
        });
        socket.on('camera', function(data){
            var img_src=data.replace("http://${ip}","");
            $("#cameraImg").attr("src","data:image/png;base64,"+img_src);
        });
    }
function back(){
    var shipinOpen2=$('input[name="shipin-checkbox"]').bootstrapSwitch('state');
    if(shipinOpen2){
        $("[name='shipin-checkbox']").bootstrapSwitch('state', false);
    }
    ws.close();
    window.location.href='${path}/index';
}
function FoodTimeList(){
    $("#food_time_list").modal('toggle');
    $(".food_list_bg").show()
    var msg={"msg":"food_time_list"}
    var json = JSON.stringify(msg);
        console.log(json);
        socket.emit("response",json+"");
}
function foodSpeedModal(){
    $("#food_speed_set").modal('toggle');
}
function setFoodSpeed(){
    var food_speed=$("input[name='food_speed']:checked").val();
    var food_chixu_time=$("#food_chixu_time").val();
    var msg = { "msg": "setFoodSpeed", "food_speed": food_speed, "food_chixu_time": food_chixu_time };
    var json = JSON.stringify(msg);
    console.log(json);
    socket.emit("response",json+"");
    foodSpeedModal();
}
function addFootTime(){
    var f_t=$("input[name='food_time']").val();
    var f_t_l=[];
    var f_t_id="food"+new Date().getTime();
    var f_w_bloon=false;
    var wweekString="";
    if(f_t!=""&&f_t!=null){
        $("input[name='food_week']:checked").each(function(index){

                if(index==0){
                    wweekString=wweekString+getWeek($(this).val());
                }else{
                    wweekString=wweekString+"、"+getWeek($(this).val());
                }
                f_w_bloon=true;
                var f_t_map={id:f_t_id,week:$(this).val(),time:f_t};
                f_t_l.push(f_t_map);

        });
        if(!f_w_bloon){
            alert("星期未选！")
        }else{
            var msg={"msg":'addFoodTime',list:f_t_l}
            var json = JSON.stringify(msg);
			console.log(json);
			socket.emit("response",json+"");
            $("#food_time_set_form")[0].reset();
            $("#food_time_set").modal('toggle');

            $(".food_time_list").append('<div class="food_time_item">' +
                '                    <div class="food_time_list_item" data-id="'+f_t_id+'">' +
                '                        <div class="food_time_list_item_left left">' +
                '                            <div class="food_time_list_item_left_week left">'+wweekString+'</div>' +
                '                            <div class="food_time_list_item_left_time right">'+f_t+'</div>' +
                '                        </div>' +
                '                        <div class="food_time_list_item_delete right" ><button type="button" class="btn btn-danger" onclick="deleteFoodTime(\''+f_t_id+'\',this)">删除</button></div>' +
                '                    </div>' +
                '                </div>')
        }
    }else{
        alert("时间不能未空！")
    }

}
function deleteFoodTime(id,_this){
    _this=$(_this);
    _this.parents(".food_time_item").remove()
    var msg={"msg":"deleteFoodTime",id:id}
    var f_t_json=JSON.stringify(msg);
    socket.emit("resopnse",f_t_json+"");
}
function mergeObject( array ) {//将硬件传输过来的喂食时间数组同一个星期合并。
        var arrayFilted = array;
        for (var af=0;af<arrayFilted.length;af++){
            for(var al=af+1;al<arrayFilted.length;al++){
                if(arrayFilted[af].id==array[al].id){
                    arrayFilted[af].week=arrayFilted[af].week+","+array[al].week;
                    arrayFilted.splice(al,1);
                    al--;
                }
            }
        }
        return arrayFilted;
}
function getWeek(week) {
    var weekObject={"0":"日","1":"一","2":"二","3":"三","4":"四","5":"五","6":"六"}
    return weekObject[week];
}
function setFoodHtml(food_time_list){
    $(".food_list_bg").hide()
    $(".food_time_list").empty();
    for(var fi=0;fi<food_time_list.length;fi++){
        var weeklist=food_time_list[fi].week.split(",");
        weeklistString="";
        for (var wi = 0; wi < weeklist.length; wi++) {
            var weekString=getWeek(weeklist[wi])
            if (wi==0){
                weeklistString=weekString;
            }else{
                weeklistString=weeklistString+"、"+weekString;
            }
        }
        $(".food_time_list").append('<div class="food_time_item">' +
            '                    <div class="food_time_list_item" data-id="'+food_time_list[fi].id+'">' +
            '                        <div class="food_time_list_item_left left">' +
            '                            <div class="food_time_list_item_left_week left">'+weeklistString+'</div>' +
            '                            <div class="food_time_list_item_left_time right">'+food_time_list[fi].time+'</div>' +
            '                        </div>' +
            '                        <div class="food_time_list_item_delete right" ><button type="button" class="btn btn-danger" onclick="deleteFoodTime(\''+food_time_list[fi].id+'\',this)">删除</button></div>' +
            '                    </div>' +
            '                </div>')
    }
}
