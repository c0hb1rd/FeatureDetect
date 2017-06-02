function jrValidateForm(form_id){
    var token=true;
    if($('#'+form_id).attr('data-message-loc')){
        var id=$("#"+form_id).attr('data-message-loc');
        $('#'+id).text('');
    }
    
    $('#'+form_id).find('input').each(function(id,val){
        
        var type=$(this).attr('type');
        var msg=$(this).attr('data-validation-message');
        if(!$(this).attr('data-validation-message')){
            msg='The value is not in desired format.';
        }
        if($(this).val()==''){
            if($(this).attr('required')){
                if(!$(this).attr('data-validation-message')){
                    msg='Please fill out this field.' ;
                }
                jrShowValidateMsg(this, msg, form_id);
                token=false;
            }
        }
        else if($(this).attr('data-custom-regex')){
            if(!jrValidateRegex(this)){
                jrShowValidateMsg(this, msg, form_id);
                token = false;
            }
        }
        else if(type=='email'){
            if(!jrValidateEmail(this)){
                jrShowValidateMsg(this, msg, form_id);
                token=false;
            }
        }
        else if(type=='password'){
            if(!jrValidatePassword(this)){
                jrShowValidateMsg(this, msg, form_id);
                token=false;
            }
        }
        else if(type=='file'){
            if(!jrValidateFile(this)){
                jrShowValidateMsg(this, msg, form_id);
                token=false;
            }
        }
    });
    return token;
}

function jrValidateRegex(elmnt){
    var regex=new RegExp($(elmnt).attr('data-custom-regex'));
    return regex.test($(elmnt).val());
}

function jrValidateFile(elmnt){
    if($(elmnt).attr('data-accepted-file-format')){
        var acceptedFormat=$(elmnt).attr('data-accepted-file-format').split(',');
        $.each(acceptedFormat, function(index,value){
            acceptedFormat[index] = (value.length && (value[0] == ',' || value[0]=='.')) ? value.slice(1) : value;
        });
        var ext=$(elmnt).val().split('.').pop();
        return ($.inArray(ext,acceptedFormat)>-1 && ext!='');
    }
    return true;
}

function jrValidatePassword(elmnt){
    var password=$(elmnt).val();
    var type=$(elmnt).attr('data-password-pattern');

    if(type==1){
        //Minimum 8 characters at least 1 Alphabet and 1 Number: ex: rohit12345
        return (/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/).test(password);
    }else if(type==2){
        //Minimum 8 characters at least 1 Alphabet, 1 Number and 1 Special Character: ex: Rohit12345
        return (/^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$/).test(password);
    }else if(type==3){
        //Minimum 8 characters at least 1 Uppercase Alphabet, 1 Lowercase Alphabet and 1 Number: ex: Rohit12345
        return (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/).test(password);
    }else if(type==4){
        //Minimum 8 characters at least 1 Uppercase Alphabet, 1 Lowercase Alphabet, 1 Number and 1 Special Character: ex: Rohit#12345
        return (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/).test(password);
    }else if(type==5){
        //Minimum 8 and Maximum 10 characters at least 1 Uppercase Alphabet, 1 Lowercase Alphabet, 1 Number and 1 Special Character:
        return (/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,10}/).test(password);
    }else if(type=='retype'){
        var repass=password;
        password=$('#'+$(elmnt).attr('data-for-password-id')).val();
        return(repass==password);
    }else{
        return true;
    }
}

function jrValidateEmail(elmnt) {
    var email=$(elmnt).val();
    var regex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return regex.test(email);
}

function jrShowValidateMsg(elmnt, msg, form_id){
    if($(elmnt).attr('data-message-loc')){
        $('#'+$(elmnt).attr('data-message-loc')).text(msg)
                                                .show()
                                                .delay(5000)
                                                .fadeOut(3000);
    }
    else if($('#'+form_id).attr('data-message-loc')){
        var id=$("#"+form_id).attr('data-message-loc');
        if($('#'+id).text()!=''){
            msg='<br>'+msg;
        }
        $('#'+id).append(msg)
                .show()
                .delay(5000)
                .fadeOut(3000);
    }
    else{
        //$('#'+id).text(msg);
        var offset = $(elmnt).offset();// "left: " + offset.left + ", top: " + offset.top
        var left=offset.left;
        var top=offset.top;
        var right=$(window).width()-$(elmnt).width()-left;

        if(right>120){
            $('<div class="jrMsgPanel jrRightMsg">\n\
                    <div class="jrMsgTail jrTailRight"></div>\n\
                </div>')
                .append(msg)
                .appendTo('body')
                .css('top', (top) + 'px')
                .css('left', parseFloat(left+$(elmnt).width()+10) + 'px')
                .delay(5000)
                .fadeOut(3000);
        }
        else if(left>120){
            var tt=$('<div class="jrMsgPanel jrLeftMsg">\n\
                        <div class="jrMsgTail jrTailLeft"></div>\n\
                    </div>')
                    .append(msg)
                    .appendTo('body')
                    .css('top', (top) + 'px')
                    .delay(5000)
                    .fadeOut(3000);
            $(tt).css('left',left-$(tt).width()-20);
            $(tt).children('.jrTailLeft').css('left',parseFloat($(tt).width())+9);
        }
        else{
            var tt=$('<div class="jrMsgPanel jrCenterMsg">\n\
                        <div class="jrMsgTail jrTailCenter"></div>\n\
                    </div>')
                    .append(msg)
                    .appendTo('body')
                    .delay(5000)
                    .fadeOut(3000);
            
            var tt_height=$(tt).height();
            var tt_width=$(tt).width();
            
            var tt_left=parseFloat(left+$(elmnt).width()-tt_width-10);
            var tt_top=parseFloat(top-tt_height-20);
            
            $(tt).css('left',tt_left)
                    .css('top',tt_top);
            
            $(tt).children('.jrTailCenter')
                    .css('left',parseFloat($(tt).width()-12)+'px')
                    .css('top',(parseFloat(tt_height)+10)+'px');
        }
    }
}