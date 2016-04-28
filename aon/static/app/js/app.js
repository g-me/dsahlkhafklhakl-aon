(function($){

//For getting CSRF token
function getCookie(name) {
          var cookieValue = null;
          if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
               var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
             }
          }
      }
 return cookieValue;
}

jQuery(document).ready(function() {

    $("#project_subcategory").hide();

    // SELECT-2  TAGS
    $(".tags").select2({

              placeholder: 'Skills',
              //tags:true,
              tokenSeparators: [',', ' '],
              ajax: {
                    url: "/ajax/skill_tags/",
                    dataType: 'json',
                    delay: 250,
                    method:'GET',
                    data: function (params) {
                       return {
                         q: params.term
                       };
                    },
                    processResults: function (data) {
                        data_result=[];
                        for(var i=0;i<data.length;i++){
                                obj={
                                    id:data[i].pk,
                                    text:data[i].fields['name']};
                                data_result.push(obj);
                        }
                        return {
                             results: data_result
                      };
                    }
              },

              cache:false,
              minimumInputLength: 1
      });

      //reject offer
    $('.btn-reject-offer').click(function () {
          var  offer_id = jQuery(this).attr("data-offer-id");
          $.get('/offer/reject/', {offer_id: offer_id}, function(data){
                    window.location.reload();
          });

      });

     // accept offer
    $('.btn-accept-offer').click(function () {
          //jQuery(this).preventDefault();
          var  offer_id = jQuery(this).attr("data-offer-id");
          $.get('/offer/accept/', {offer_id: offer_id}, function(data){
                    window.location.reload();
          });

      });


    // project form
    $("#project_category").change(function () {
         var param=this.value;
         var el=jQuery("#project_subcategory");
         el.html("");
         el.append("<option value='-1' selected='selected'>Select a job (Optional)</option>");

        jQuery.ajax({
            method: "GET",
            url: "/ajax/project/sub_categories/",
            dataType:"json",
            data:{'q':param},
            success: function (data) {
                for(var i=0;i<data.length;i++){
                    el.append("<option value="+data[i].fields['slug']+" >"+data[i].fields['name']+"</option>");
                }
                el.show();
            },
            error: function (data) {
             console.log('error');
             console.log(data)
            }

        })
     });


    $("#project_status_options").change(function () {
         var new_status=this.value;
         var  project_id = $(this).attr("data-project-id");
        console.log(new_status);

        jQuery.ajax({
            method: "GET",
            url: "/ajax/project/update_progress",
            dataType:"json",
            data:{'project_status':new_status,'project_id':project_id},
            success: function (data) {


                //if (new_status==101){
                //    // request peer review
                //    peers=data['collaborators'];
                //    if(peers){
                //        console.log(peers);
                //        var el=jQuery("#project_review_modal");
                //        var old_el=jQuery("#change_status_modal");
                //        old_el.modal('hide');
                //        el.modal('show');
                //
                //    }
                //
                //}
                redirect_url=data['message'];
                window.location.href = redirect_url;

            },
            error: function (data) {
                console.log('error');
                console.log(data)
            }

        })

     });

    $("#math_me_btn").click(function (e) {
         e.preventDefault();

        var type=jQuery('#project_category').val();
        var job=jQuery('#project_subcategory').val();
        var skills=jQuery('#offer_skills'). val();

        jQuery.ajax({
            method: "GET",
            url: "/ajax/project/filter/",
            dataType:"json",
            data:{
                'category':type,
                'job':job,
                'skills':skills
            },
            success: function (data) {

                var el=jQuery('#filter_result_modal');
                var el_body=jQuery('#filter_result_modal .content');
                el_body.html("");
                if(data.length>0){

                     for(var i=0;i<data.length;i++){
                        var title=data[i].fields['title'];
                        var slug=data[i].fields['slug'];
                        var created=data[i].fields['created'];
                        var id=data[i].pk;
                         var dt=new Date(created);
                         var date_formated = new Date(dt).toLocaleDateString('en-GB', {
                                day : 'numeric',
                                month : 'short',
                                year : 'numeric'
                            }).split(' ').join('-');

                         var _templete="<div class='app-project-list-item' data-project-id='"+id+"'>"+
                                            "<i class='result_select_btn' >&#10004;</i>"+
                                            "<div class='title'>"+title+"</div> " +
                                            "<span class='date_time'>"+date_formated    +"</span>"+
                                        "</div>";
                         el_body.append(_templete);



                    }
                }else{
                      var _templete="No Match Found!";

                    el_body.append(_templete);

                }


                el.modal('show');

            },
            error: function (data) {
                 console.log(data)
            }

        })

    });

    $(document).on('click', '.result_select_btn', function (){
                 var el=jQuery('#filter_result_modal');
                 var pid=jQuery(this).parent().attr("data-project-id");
                 jQuery(this).css({"background-color": 'green' });

                 jQuery.ajax({
                    method: "GET",
                    url: "/ajax/project/get",
                    dataType:"json",
                    data:{
                        'q':pid
                    },
                    success: function (data) {
                        var el=jQuery('#selected_offer');
                        var el2=jQuery('#offer_filter_options');
                        el2.hide();
                        var slug= data.fields['slug'] ;
                        var title= data.fields['title'] ;
                        var created= data.fields['created'] ;
                        var dt=new Date(created);
                        var date_formated = new Date(dt).toLocaleDateString('en-GB', {
                                    day : 'numeric',
                                    month : 'short',
                                    year : 'numeric'
                                }).split(' ').join('-');

                        var _templete="<div> " +
                                            "<i class='icon icon-pencil' id='change_match'></i> " +
                                            "<i class='icon icon-remove' style='float:right' id='remove-selected-offer'></i> " +
                                       "</div>" +
                                        "<a href='/projects/"+slug+"'" +"class='dashboard-project-title' >"+
                                            title +
                                        "</a>"+
                                        "<div>"+date_formated+"</div>"  ;

                        el.html(_templete);
                        el.attr('data-project-id',pid);
                        el.css({"display":'block'});


                        var content=jQuery('#action_btns');
                        content.html("<input style='margin-left: 250px;' id='post_project_btn' class='btn btn-info' type='submit' value='Post' />")

                    },
                    error: function (data) {
                         console.log(data)
                    }

                });

                setTimeout(function(){  el.modal('hide'); }, 100);

    });

    $(document).on('click', '#post_project_btn', function (e){
        e.preventDefault();
        var csrftoken = getCookie('csrftoken');
        var pid=$("#selected_offer").attr("data-project-id");
        var title=$('input[name=request_title]').val();
        var category=$('select[name=request_category]').val();
        var description=$('textarea[name=request_description]').val();
        var skills=$('select[name=request_skills]').val();

        if (csrftoken && title && category){
             $.ajax({
            method: "POST",
            url: "/ajax/post/requestoffer/",
            data: {
                'csrfmiddlewaretoken':csrftoken,
                'offer_id': pid,
                'title': title,
                'category': category,
                'description': description,
                'skills': skills
            },
            success: function (json) {
                console.log(json); // another sanity check
                if(json['status']=='success'){
                    var el=$('.messages');
                    el.append("<li class='success' >Your Offer Request  Pair Posted Successfully!</li>");

                }

            },

            error: function (xhr,errmsg,err) {
                // provide a bit more info about the error to the console
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
        }

    });

    $(document).on('click', '#change_match', function (e){
        e.preventDefault();
        var el=jQuery('#search_offer');
        el.css({'display':'block'});

        var el2=jQuery('#offer_filter_options');
        el2.show();
    });

    $(document).on('click', '#remove-selected-offer', function (e){
        e.preventDefault();
        console.log('remove project');
        var el=jQuery('#search_offer');
        el.css({'display':'block'});

        var el2=jQuery('#selected_offer');
        el2.css({'display':'none'});

        var el3=jQuery('#offer_filter_options');
        el3.show();
    });

    $(document).on('click',"#search_offer", function () {
        var type=$('#project_category').val();
        var job=$('#project_subcategory').val();
        var skills=$('#offer_skills').val();

        $.ajax({
            method: "GET",
            url: "/ajax/project/filter/",
            dataType: "json",
            data: {
                'category': type,
                'job': job,
                'skills': skills
            },
            success: function (data) {

                var el = jQuery('#filter_result_modal');
                var el_body = jQuery('#filter_result_modal .modal-body');
                el_body.html("");
                 if(data.length>0) {
                     for (var i = 0; i < data.length; i++) {
                         var title = data[i].fields['title'];
                         var slug = data[i].fields['slug'];
                         var created = data[i].fields['created'];
                         var id = data[i].pk;
                         var dt = new Date(created);
                         var date_formated = new Date(dt).toLocaleDateString('en-GB', {
                             day: 'numeric',
                             month: 'short',
                             year: 'numeric'
                         }).split(' ').join('-');

                         var _templete = "<div class='app-project-list-item' data-project-id='" + id + "'>" +
                             "<i class='result_select_btn' >&#10004;</i>" +
                             "<div class='title'>" + title + "</div> " +
                             "<span class='date_time'>" + date_formated + "</span>" +
                             "</div>";


                         el_body.append(_templete);
                     }
                 }else{
                       var _templete="No Match Found!";

                    el_body.append(_templete);
                 }
                el.modal('show');

            },
            error: function (data) {
                console.log(data)
            }
        });
    });

    $(document).on('click', '#post-request', function (e){
        e.preventDefault();

        //Prepare csrf token
        var csrftoken = getCookie('csrftoken');
        var title=$('input[name=quick_request_title]').val();
        var category=$('select[name=quick_request_category]').val();
        var description=$('textarea[name=quick_request_description]').val();
        var skills=$('select[name=qucik_request_skills]').val();

        if (csrftoken && title && category){
             $.ajax({
            method: "POST",
            url: "/ajax/project/new/",
            dataType: 'json',
            data: {
                'csrfmiddlewaretoken':csrftoken,
                'title': title,
                'category': category,
                'description': description,
                'skills': skills
            },
            success: function (json) {
                console.log(json); // another sanity check
                if(json['status']=='success'){

                    var el=$('.messages');
                    el.append("<li class='success' >Success!!</li>");

                    var el2= $('#new_project_modal');
                    el2.modal('hide');


                }

            },
            error: function (xhr,errmsg,err) {
                // provide a bit more info about the error to the console
                console.log(xhr.status + ": " + xhr.responseText);
            }
        });
        }



    });

    // Accordion UI
    $("#InExchangeForAccordion").on({
         'hidden.bs.collapse': function (e) {
            var el=$('#action_btn_post');
            el.css({"display":'block'});
         },

         'shown.bs.collapse':function (e) {
             var el=$('#action_btn_post');
             el.css({"display":'none'});
         }

    });


    // VALIDATIOINS
    $("#ro-form").validate({
        rules:{
            'request_title':{
                    'required':true,
                    'minlength':10
            },
            'request_category':{
                'required':true
            },
            'request_description':{
                'minlength':25
            }
        },
        messages:{
            'request_title':{
                    'required':'The Title is required!',
                    'minlength':"Title must consist of at least 10 characters"
            },
            'request_category':{
                'required':'Please Select Catagory Of Project'
            },
            'request_description':{
                'minlength':"Title must consist of at least 25 characters"
            }
        }
    });


});

})(jQuery);
