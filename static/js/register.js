/*注册页面的js检查函数*/
$(function () {
	/*定义个输入框默认状态值*/
	var error_name = false;
	var error_password = false;
	var error_check_password = false;
	var error_email = false;
	var error_check = false;

	/*失去焦点时候，触发函数*/
	$('#user_name').blur(function () {
		check_user_name();
	});

	$('#pwd').blur(function () {
		check_pwd();
	});

	$('#cpwd').blur(function () {
		check_cpwd();
	});

	$('#email').blur(function () {
		check_email();
	});

	$('#allow').click(function () {
		/*根据勾选框的状态进行判断*/
		if ($(this).is(':checked'))
		{
			error_check = false;
			$(this).siblings('span').hide();
		}
		else
		{
			error_check = true;
			$(this).siblings('span').html('请勾选同意')
			$(this).siblings('span').show()
		}
	});

	/*定义检查用户名的函数*/
	function check_user_name() {
		/*获取输入框的值的长度*/
		var len = $('#user_name').val().length
		/*比较长度，如果长度不够，则报错*/
		if (len<5 || len>20)
		{
			/*显示报错提示信息块，并传入新的报错信息*/
			$('#user_name').next().html('请输入5-20个字符的用户名')
			$('#user_name').next().show()
			/*将默认值设置为true*/
			error_name = true
		}
		else
		{
			/*满足要求*/
			$('#user_name').next().hide();
			error_name = false;
		}
	}

	function check_pwd() {
		var len = $('#pwd').val().length;
		if (len<8 || len>20)
		{
			$('#pwd').next().html('密码最少8位，最长20位');
			$('#pwd').next().show();
			error_password = true;
		}
		else
		{
			$('#pwd').next().hide();
			error_password = false;
		}
	}

	function check_cpwd() {
		var pass = $('#pwd').val();
		var cpass = $('#cpwd').val();

		if (pass != cpass)
		{
			$('#cpwd').next().html('两次输入的密码不一致')
			$('#cpwd').next().show();
			error_check_password = true;
		}
		else
		{
			$('#cpwd').next().hide();
			error_check_password = false;
		}
	}

	function check_email() {
		var re = /^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;

		if (re.test($('#email').val()))
		{
			$('#email').next().hide();
			error_email = false;
		}
		else
		{
			$('#email').next().html('你输入的邮箱格式不正确');
			$('#email').next().show();
			error_email = true;
		}
	}

	// 表单提交的时候，触发所有的检查函数
	$('.reg_form').submit(function () {
        check_user_name();
        check_pwd();
        check_cpwd();
        check_email();

        /*所有检查函数执行完成，并且所有的error_xx值为false，代表检查正确*/
        if (error_name == false && error_password == false && error_check_password == false && error_email == false && error_check ==false)
        {
            return true;
        }
        else
        {
            return false;
        }
    });

});