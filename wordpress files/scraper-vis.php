<?php
/* Template Name: Scraper visualisation */ 
wp_enqueue_script( 'jquery' );
get_template_part( 'singular' );

?>
<script>
	scrape = undefined;
	jQuery(document).ready(function( $ ) {
		scrape = function() {
			document.getElementById("loadingindicator").style.display = "block";
			let query = $('#scrapequery').val();
			let url = "http://18.206.118.135/wp-json/scraper/v1/visualise?query="+query
			console.log('query: ' + query);
			console.log('url: ' + url);
			$.ajaxSetup({timeout:0}); //in milliseconds, 0 means no timeout
			$.get( url, function( data ) {
				console.log(data);
				console.log( "Load was performed." );
				console.log('received: ' + data.length + ' items')
				console.log('first item is : ' + data[0])
				var tableRef = document.getElementById('resultstable').getElementsByTagName('tbody')[0];
				// Insert a row in the table at the last row

				for(var i = 0; i < data.length; i++) {
					var newRow   = tableRef.insertRow();
					var obj = data[i];
					cells = []
					for (var j = 0;j < 8; j++) {
						// Insert a cell in the row at index j
						cells.push(newRow.insertCell(j));
					}
					cells[0].innerHTML = obj.full_name
					cells[1].innerHTML = obj.year
					cells[2].innerHTML = obj.speciality
					cells[3].innerHTML = obj.experience
					cells[4].innerHTML = obj.languages
					cells[5].innerHTML = obj.city_state
					cells[6].innerHTML = obj.journal
					cells[7].innerHTML = obj.query
				}
				document.getElementById("loadingindicator").style.display = "none";

			});
		}

	});

</script>



