$(document).ready(function() { // opens reviews
    $(document).on('click',".product_display", function(){
        if ($("div").hasClass("expanded") === true){
            console.log("You can only expand one")
            $(this).removeClass("expanded");
            $(this).children(".reviews").removeClass("visable");
            $(this).parent().removeClass("expandedParent");
        }
        else{
            if ($(this).hasClass("expanded")){
                return
            }
            else {
                $(this).addClass("expanded");
                $(this).children(".reviews").addClass("visable");
                $(this).parent().addClass("expandedParent");
            }
        }
    })
});

// function closeEdit(){   // closes the reviews
//     console.log("close")
//     $("div").removeClass("expanded");
//     $("div").removeClass("expandedParent");
//     // $(".modifyButtons").remove();
//     $("div").removeClass("expanded");
//     $(".reviews").removeClass("visable");
// };