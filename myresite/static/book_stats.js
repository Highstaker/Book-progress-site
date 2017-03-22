$(function() {

    /////////////////
    ///////////CSRF token for DJANGO
    ////////////////
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    /////////////////
    /////////END  handling CSRF token
    ////////////////////

    //script for checkboxes and forms
    var COLOR_TRANS = "orange";
    var SYMBOL_TRANS = "O";
    var COLOR_ERROR = "white";
    var SYMBOL_ERROR = "Err";
    var COLOR_TRUE = "green";
    var SYMBOL_TRUE = "V";
    var COLOR_FALSE = "red";
    var SYMBOL_FALSE = "X";

    $(document).ready(function() {
        console.log("Script started");
        $(".editable_checkbox").click(function(event) {
            var id = $(this).attr('id');
            var parse = id.split("-");
            var page_number = parse[0];
            var property = parse[1];

            var set_checkbox = function(elem, val) {
                //toggles what the checkbox looks like
                var text = elem.text().trim();

                if (val === 0) {
                    elem.css({ "background-color": COLOR_FALSE });
                    elem.text(SYMBOL_FALSE);
                } else if (val == 1) {
                    elem.css({ "background-color": COLOR_TRUE });
                    elem.text(SYMBOL_TRUE);
                } else if (val == -1) {
                    elem.css({ "background-color": COLOR_TRANS });
                    elem.text(SYMBOL_TRANS);
                } else if (val == -2) {
                    elem.css({ "background-color": COLOR_ERROR });
                    elem.text(SYMBOL_ERROR);
                }
            };

            //set to wait trans state
            var style_buf = { "background-color": $(this).css("background-color") };
            var text_buf = $(this).text();
            set_checkbox($(this), -1);

            $.ajax({
                url: "/api1/book/" + book_id + "/page/" + page_number + "/set_page_property",
                type: "POST",
                dataType: "Json",
                context: $(this), //Specifies the "this" value for all AJAX related callback functions; needed, cuz callbacks don't get "this" on their own.
                data: JSON.stringify({ "page_number": page_number, "property": property }),
                success: function(data, status) {
                    console.log("Success!"); //debug
                    set_checkbox($(this), data.value);
                },
                error: function(xhr, status, error) {
                    console.log("Error!"); //debug
                    console.log(error); //debug
                    set_checkbox($(this), -2);
                }
            });
        }); //editable_checkbox click

        $("#insert-page-form-toggle-button").click(function() {
            $("#insert-page-form").slideToggle("fast", "linear");
        });
        $("#insert-page-form").hide(); //The benefit of this version over style "display:none": if jquery disappears, we default to form being shown.

        $("#insert-page-form").submit(function(e) {
            console.log("#insert-page-form"); //debug

            var insert_at = $("#id_insert_at").val();
            var pages_amount = $("#id_amount").val();
            console.log(insert_at + " " + pages_amount); //debug

            $.ajax({
                url: add_pages_url,
                type: "POST",
                dataType: "Json",
                context: $(this), //Specifies the "this" value for all AJAX related callback functions; needed, cuz callbacks don't get "this" on their own.
                data: JSON.stringify({ "insert_at": insert_at, "pages_amount": pages_amount }),
                success: function(data, status) {
                    console.log("Insertion success!"); //debug
                    console.log(data); //debug
                    location.reload();
                },
                error: function(xhr, status, error) {
                    console.log("Insertion error!"); //debug
                    console.log(status); //debug
                    console.log(error); //debug
                }
            });

            return false; // prevents refresh
        }); //$("#insert-page-form").submit

        $("#validate-pages-button").click(function() {
            $.ajax({
                url: validate_pages_url,
                type: "POST",
                dataType: "Json",
                context: $(this), //Specifies the "this" value for all AJAX related callback functions; needed, cuz callbacks don't get "this" on their own.
                // data: JSON.stringify({"insert_at": insert_at, "pages_amount": pages_amount}),
                success: function(data, status) {
                    console.log("Validation success!"); //debug
                    console.log(data); //debug
                    location.reload();
                },
                error: function(xhr, status, error) {
                    console.log("Validation error!"); //debug
                    console.log(status); //debug
                    console.log(error); //debug
                }
            }); //ajax

        }); //$("#validate-pages-button").click

        $(".page-delete-button").click(function(event) {
            var id = $(this).attr('id');
            var parse = id.split("-");
            var page_number = parseInt(parse[0]);

            $.ajax({
                url: delete_pages_url,
                type: "POST",
                dataType: "Json",
                context: $(this), //Specifies the "this" value for all AJAX related callback functions; needed, cuz callbacks don't get "this" on their own.
                data: JSON.stringify({ "pages_to_delete": page_number }),
                success: function(data, status) {
                    console.log("Deletion success!"); //debug
                    console.log(data); //debug
                    location.reload();
                },
                error: function(xhr, status, error) {
                    console.log("Deletion error!"); //debug
                    console.log(status); //debug
                    console.log(error); //debug
                }
            }); //ajax
        }); //$(".page-delete-button").click
    }); //ready
}); //$()
