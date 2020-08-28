// Method: POST, PUT, GET etc
// Data: array("param" => "value") ==> index.php?param=value
add_action( 'rest_api_init', function () {
    //Path to ajax function
    register_rest_route( 'scraper/v1', '/visualise/', array(
            'methods' => 'GET', 
            'callback' => 'visualise_php' 
    ) );
});
// The function we set in the callback
function visualise_php(){
	$scripturl = 'http://127.0.0.1:5000/scrape/healthnews';
	if (isset($_GET['query'])) {
        $query = $_GET['query'];
		$scripturl = $scripturl . '?query='.$query;
    }
	$response = wp_remote_get( $scripturl ,
		array(
			'timeout'     => 2000
		));
	if ( is_array( $response ) ) {
		$header = $response['headers']; // array of http header lines
		$body = $response['body']; // use the content
		return rest_ensure_response(json_decode($body, true));
	}
	return rest_ensure_response( json_decode('{"error": "nodata"}', true) );
}
