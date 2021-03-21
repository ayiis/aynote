$(()=>{
    window.common = {
        api_post: (args) => {
            $.ajax({
                type: "POST",
                contentType: "application/json; charset=UTF-8",
                url: args.url,
                data: JSON.stringify(args.data || {}),
                dataType: "json",
                success: function(res) {
                    args.success(res);
                },
                error: function(err) {
                    if (args.error) {
                        args.error(err);
                    } else {
                        $.notify("req error: " + err.responseText, "error");
                        console.log("Url fail (", args.url, "):", err.responseText);
                    }
                }
            });
        },
        get_date_range: (start_date, end_date)=> {
            start_date = new Date(start_date);
            end_date = new Date(end_date);
            let arr = [];
            let dt = new Date(start_date);
            while (dt <= end_date) {
                arr.push(dt.toISOString().slice(0,10));
                dt.setDate(dt.getDate() + 1);
            }
            return arr;
        },
        get_datetime_string: ()=> {
            let now = new Date();
            let mm = now.getMonth() + 1;
            let dd = now.getDate();

            return [
                now.getFullYear(),
                ("0" + (now.getMonth() + 1)).slice(-2),
                ("0" + now.getDate()).slice(-2),
            ].join("-") + " " + [
                ("0" + now.getHours()).slice(-2),
                ("0" + now.getMinutes()).slice(-2),
                ("0" + now.getSeconds()).slice(-2)
            ].join(":");
        },
        scroll_to_ele: (ele)=> {
            let scroll_top = ele.offset() ? ele.offset().top : 0;
            $([document.documentElement, document.body]).scrollTop(scroll_top);
        },
    }

    $(document.body).on("click", "button[link]", function() {
        window.location.href = $(this).attr("link");
    });

});
