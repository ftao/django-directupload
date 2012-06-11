function getCookie(c_name) //TODO possibly replace with the jquery cookie plugin
{
    var i,x,y,ARRcookies=document.cookie.split(";");
    for (i=0;i<ARRcookies.length;i++)
    {
      x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
      y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
      x=x.replace(/^\s+|\s+$/g,"");
      if (x==c_name)
      {
        return unescape(y);
      }
    }
}

function add_csrf(jqXHR, settings) {
    jqXHR.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
}


function make_form_uploader($, selector, options_url, determine_name_url) {
    
    function add(event, data) {
        var file = data.files[0];
        var id = $(this).attr('id');

        if (!file) return; //some browsers improperly trigger the event for non file fields
        
        //determine the target path and update post data if our backend requires
        var upload_to = $(event.currentTarget).attr('data-upload-to') || '';
        if (upload_to.substr(-1) != '/') {
            upload_to += '/';
        }
        
        jQuery.ajax({
            type    : 'POST',
            //async   : false,
            dataType: 'json',
            url     : determine_name_url,
            beforeSend : add_csrf,
            data    : {filename: file.name,
                       upload_to: upload_to},
            success : function(post_data) {
                data.formData = post_data;
                file.path = post_data['targetpath'];
                data._direct_upload_inited = true;
//                data.submit();
            }
        });
    }
    
    function submit(e, data) {
        if(!data._direct_upload_inited){
          return false;
        }
    }

    $.getJSON(options_url, function(data) {
        var options = $.extend({
            'async': true,
            'type': 'POST',
            'autoUpload' : true,
        }, data);
        $(selector).fileupload(options);
        $(selector).bind('fileuploadadd', add);
        $(selector).bind('fileuploadsubmit', submit);
    });
}


