var $messages = $('.messages-content'),
    d, h, m,
    i = 0;
const message_input = document.getElementById("message-input")

$(window).load(function() {
  $messages.mCustomScrollbar();
  setTimeout(async function() {
    await fakeMessage();
  }, 100);
});


function updateScrollbar() {
  $('.messages-content').animate({ scrollTop: $('.messages-content').prop("scrollHeight")}, 500);
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  $('.message-input').val(null);
  updateScrollbar();

  setTimeout(async function() {
    await fakeMessage();
  }, 500);
}

$('.message-submit').click(async function() {
  const choices = get_checked_symtom()
  if (choices.length > 0){
    await postChoices(choices)
  }
  insertMessage();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
})

async function getInfor(){
  const infor = await getNextQuestion(user_id)
  return infor.data
}

async function fakeMessage() {
  if ($('.message-input').val() != '') {
    return false;
  }
  const infor = await getInfor()
  const history = infor.history

  const question = history[history.length - 1]

  const is_multiple  = question.is_multiple

  $('<div class="message loading new"><figure class="avatar"><img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/156381/profile/profile-80.jpg" /></figure><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();
  removeSytoms()
  
  if (infor.result == null){
    setTimeout(function() {
      $('.message.loading').remove();
      console.log(question.question)
      $('<div class="message new"><figure class="avatar"><img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/156381/profile/profile-80.jpg" /></figure>' + question.question + '</div>').appendTo($('.mCSB_container')).addClass('new');
      updateScrollbar();
      console.log(question.choices)
      addSystoms(question.choices, is_multiple);
      
    }, 100 + (Math.random() * 20) * 100);
  }else{
    setTimeout(function() {
      $('.message.loading').remove();
      console.log(infor.result)
      $('<div class="message new"><figure class="avatar"><img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/156381/profile/profile-80.jpg" /></figure>' + infor.result + '</div>').appendTo($('.mCSB_container')).addClass('new');
      updateScrollbar();
    }, 100 + (Math.random() * 20) * 100);
  }
  

}
function get_checked_symtom(){
  const symtomBtns = document.getElementsByClassName("symtom-check")
  const symtoms = []

  for (x = 0 ; x< symtomBtns.length; x++){
    if (symtomBtns[x].checked){
      symtoms.push(symtomBtns[x].value)
    }
  }
  return symtoms
}

function addSystoms(symtoms, is_multiple) {
  for (x =0 ; x < symtoms.length; x++){
    $(`<div class="col">
        <div class = "systom-item">
          <input type="checkbox" class="btn-check symtom-check" id="btncheck${x}" autocomplete="off" value ="${symtoms[x]}" >
          <label class="btn btn-outline-light systom-infor" for="btncheck${x}">${symtoms[x]}</label>
        </div>
      </div>`).appendTo($('.systoms'));
  }

  const symtomBtns = document.querySelectorAll(".symtom-check")
  symtomBtns.forEach(symtomBtn => {
    symtomBtn.addEventListener('click', async function handleClick(event) {
      const choices = get_checked_symtom()
      if (!is_multiple && (choices.length > 1)){
        symtomBtn.checked = false
      }else{
        message_input.value = choices.join(", ")
      }
    });
  });
}

function removeSytoms(){
  removeAllChildNodes($('.systoms')[0])
}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
 
}

// addSystoms();

const user_infor = document.getElementById('user-infor')
const base_url = window.location.origin;
const user_id = user_infor.getAttribute('user_id')

async function getNextQuestion(){
  const response = await fetch(`${base_url}/users/${user_id}`)
    .then((response) => response.json())
  return response;
}

async function postChoices(choices){
  const response = await fetch(`${base_url}/users/${user_id}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(choices) // body data type must match "Content-Type" header
  });
  return response.json();
}