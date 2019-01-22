<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<link rel="stylesheet" type="text/css" href="css/styles.css">
	<link href="https://fonts.googleapis.com/css?family=Nunito+Sans" rel="stylesheet">

	<title>PyJudge</title>
</head>
<body>
<h1>Probleam</h1>
<p> {{question}} </p>

<div class="shift-center">
					
					<a href="{{link_to_download}}">Download Test Case</a>
				</div>

<div class="column submit-column">
				<div class="shift-center">
					<!--Submission-->
					<form action="{{number}}/upload", method = "post", enctype = "multipart/form-data">   
					   <!-- URL can be added where file is to be stored -->
					   <p>All submissions will be tested on the already mentioned criterias. 
					   To read the criterias, click <a href="#">here</a>.
					   You have to submit your code in a file.
					   You can submit the code in any language.
					   You can upload the file below.</p>
					   <input type="file" name="upload">
					   <input type="submit" value = "Start upload">
					</form>
				</div>
			</div>

</body>	
</html>