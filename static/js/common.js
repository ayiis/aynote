(()=>{
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
        scroll_to_ele: (ele)=> {
            let scroll_top = ele.offset() ? ele.offset().top : 0;
            $([document.documentElement, document.body]).scrollTop(scroll_top);
        },
    }

    $("body").on("click", "button[link]", function(){
        // window.location($(this).attr("link"));
        window.location.href = $(this).attr("link");
    });

})();
