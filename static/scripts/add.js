var checkbox = document.querySelector("#checkbox");
var date = document.querySelector(".date");
var views = document.querySelector(".views");
var selector = document.querySelector('.select');
var s_file = document.querySelector('input[value="file"]');
var s_img = document.querySelector('input[value="img"]');
var s_txt= document.querySelector('input[value="txt"]');
var d_file = document.querySelector('.file');
var d_img = document.querySelector('.image');
var d_txt= document.querySelector('.text');

d_file.style.display = s_file.checked ? 'block' : "none";
d_img.style.display = s_img.checked ? 'block' : "none";
d_txt.style.display = s_txt.checked ? 'block' : "none";
views.style.display = 'none';

checkbox.addEventListener('change', function() {
  if (this.checked) {
    date.style.display = 'none';
    views.style.display = 'block';
  } else {
    date.style.display = 'block';
    views.style.display = 'none';
  }
});


selector.addEventListener('change', function() {
    d_file.style.display = s_file.checked ? 'block' : "none";
    d_img.style.display = s_img.checked ? 'block' : "none";
    d_txt.style.display = s_txt.checked ? 'block' : "none";
  });

  function updateSize() {
    var file = document.getElementById("uploadInput").files[0];
    if((file.size / 1024) / 1024 > 10){
      document.querySelector('#answer').innerHTML = "file size more then 10Mb"
    }else if(document.querySelector('#answer').innerHTML.length !== 0){
      document.querySelector('#answer').innerHTML = "norm"
    }
    
  }
  
  document.getElementById('uploadInput').addEventListener('change', updateSize);