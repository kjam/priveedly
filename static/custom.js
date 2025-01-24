function mark_read_later(entry_id, entry_type) {
      $.ajaxSetup({
   	   headers: { 
	      'X-CSRFToken': Cookies.get('csrftoken'),
   	   }
      });

   $.post("/feeds/mark-read-later/", 
	   {'entry_id': entry_id, 'entry_type': entry_type});
}

function unmark_read_later(entry_id, entry_type) {
      $.ajaxSetup({
   	   headers: { 
	      'X-CSRFToken': Cookies.get('csrftoken'),
   	   }
      });

   $.post("/feeds/unmark-read-later/", 
	   {'entry_id': entry_id, 'entry_type': entry_type});
}

function mark_interesting(entry_id, entry_type) {
      $.ajaxSetup({
   	   headers: { 
	      'X-CSRFToken': Cookies.get('csrftoken'),
   	   }
      });

   $.post("/feeds/mark-interesting/", 
	   {'entry_id': entry_id, 'entry_type': entry_type});
}

function mark_read() {
      var IDs = [];
      var entry_types = [];
      $("h3").each(function(){ 
	      IDs.push(this.id); 
	      entry_types.push($(this).attr("entry_type")); });
      var IDsString = IDs.join(",");
      var typesString = entry_types.join(",");
      $.ajaxSetup({
   	   headers: { 
	      'X-CSRFToken': Cookies.get('csrftoken'),
   	   }
      });

      $.post("/feeds/mark-read/", 
	      {"id_list": IDsString,
	       "entry_types": typesString})
	.done(function(){
            document.body.scrollTop = document.documentElement.scrollTop = 0;
	    location.reload();
        });
} 


