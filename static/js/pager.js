// for bootstrap 4.3.1
window.pager = {
    init_pagination: function(args) {
        // 初始化 分页控件, 一个页面可以使用多个
        let self = this;
        let this_pager = {
            "ele": args.ele,
            "callback": args.callback,

            // 默认值
            "total_count": 0,   // 如果没有返回，默认 0 条结果
            "page_index": 1,    // 默认第 1 页
            "page_size": args.page_size || 10,    // 默认 10 条
            "total_show": args.total_show || 5,    // 默认显示 5 个翻页按钮
        };
        for(let e in self) {
            this_pager[e] = self[e];
        }

        this_pager.ele.empty().append(
            "<nav>" +
                "<ul class=\"pagination float-left\"></ul>" +
                "<ul class=\"pagination float-left\" style=\"padding-left:.5rem;\"></ul>" +
            "</nav>"
        );
        this_pager.pagination_ele = this_pager.ele.find("ul:eq(0)");
        this_pager.pagination_jump = this_pager.ele.find("ul:eq(1)");

        this_pager.ele.on("click", "a", function() {
            let page_index = Number($(this).attr("val")) || 1;
            this_pager.callback && this_pager.callback(page_index);
            return false;
        });
        this_pager.ele.on("keydown", ".page-jump", function(event) {
            if(event.keyCode == 13) {
                let pageno = $(this).val();
                pageno = Number(pageno) || 1;
                this_pager.callback(pageno);
                return false;
            }
        });

        return this_pager;
    },
    init_document_listener: function() {
        let self = this;
        $(document).keydown(function (event) {
            event = event || window.event;
            if(!self.callback) {
                return;
            }
            switch(event.keyCode) {
                case 37: self.callback(self.page_index - 1); break; // LEFT
                // case 38: x = x - 10; $("selector").css("top", x + "px"); break;  // UP
                case 39: self.callback(self.page_index + 1); break;    // RIGHT
                // case 40: x = x + 10; $("selector").css("top", x + "px"); break;  // DOWN
                // case 13: x = x + 10; $("selector").css("top", x + "px"); break;  // ENTER
                default: break;
            }
        });
    },
    touch_pagination: function(total_count, page_index) {
        let self = this;
        self.total_count = total_count || self.total_count;
        self.page_index  = page_index  || self.page_index;
        let pagination_setting = self.cal_pagination_page(
            self.total_count,
            self.page_index
        );
        let total_page = pagination_setting[pagination_setting.length - 1];
        let html_list = [];
        for( let i = 0 ; i < pagination_setting.length ; i++ ) {
            let li_string = "";
            let val = pagination_setting[i];
            if (pagination_setting[i] == "") {
                li_string = '<li class="page-item"><p class="page-link" style="background-color:#eee;height:2.4rem;">&nbsp;</p></li>';
            } else if (i == 0) {
                li_string = '<li class="page-item"><a class="page-link" href val="' + val + '"> ' + val + ' « </a></li>';
            } else if (i == pagination_setting.length - 1) {
                li_string = '<li class="page-item"><a class="page-link" href val="' + val + '"> » ' + val + ' </a></li>';
            } else if (pagination_setting[i] == self.page_index) {
                li_string = '<li class="page-item active"><a class="page-link" href val="' + val + '"> ' + val + ' </a></li>';
            } else {
                li_string = '<li class="page-item"><a class="page-link" href val="' + val + '"> ' + val + ' </a></li>';
            }
            html_list.push(li_string);
        }
        self.pagination_ele.empty().append(html_list.join(""));
        self.pagination_jump.empty().append([
            '<li class="page-item"><input style="width:2rem;line-height:2.15rem;border:1px solid #eee;border-radius:0.25rem;" class="page-jump" placeholder="GO"/></li>',
            '<li class="page-item"><div style="padding:.5rem" class="text-center"><span style="color:#bbb">' + self.total_count + ' 条记录, 共' + total_page + '页</span></div></li>',
        ]);
    },
    cal_pagination_page: function(total_count, page_index) {
        let self = this;
        let first_page = 1;
        let last_page = Math.ceil(total_count / self.page_size);
        page_index = Math.min(page_index, last_page);
        page_index = Math.max(page_index, first_page);
        let start_page = page_index - parseInt(self.total_show / 2);
        let end_page = page_index + Math.round(self.total_show / 2);

        let page_content = [first_page];
        for( let i = start_page; i <= page_index; i++ ) {
            page_content.push(i < first_page ? "" : i );
        }
        for( let i = page_index + 1; i < end_page; i++ ) {
            page_content.push(i > last_page ? "" : i);
        }
        page_content.push(last_page);
        return page_content;
    },
};
