$(function () {
	//获取幻灯片整体
	var $slide = $('.slide');
	//获取幻灯片元素
	var $li = $('.slide_pics li');
	//获取点击前后换页的元素标签
	var $prev = $('.prev');
	var $next = $('.next');
	//定义定时器变量
	var timer = null;
	//定义开关，防止前后点击按钮的暴力操作，导致幻灯片还没有移动过来，就又点击下一张幻灯片
	var ismove = false;
	//获取幻灯片个数，用于添加下面的小标点
	var $len = $li.length;
	// 获取标点元素标签，通过js加入子标签
	var $poinsts_con = $('.points');
	//循环动态添加ponit下的节点
	for(var i=0;i<$len;i++)
	{
		//定义新的points下的li元素标签
		var $newli = $('<li>');
		// 给第一个li标签添加active类
		if( i==0 )
		{
			$newli.addClass('active');
		}
		$newli.appendTo($poinsts_con);
	}

	//判断此前找到的幻灯片标签，将索引不是第一个的其他所有幻灯片，放置于幻灯片区域的最右边，只显示第一张图片
	$li.not(':first').css({'left': 760});

	//获取points下的小圆点,需要等上面动态添加之后再获取，否则找不到
	var $points = $('.points li');

	//初始化索引值，要运动过来的幻灯片的索引值
	var nowli = 0;

	//初始化索引值，要离开的幻灯片的索引值
	// 通过这两个索引值，进行幻灯片的选择
	var prevli = 0;

	//编写小圆点点击的动作函数
	$points.click(function () {
		// 当前点击圆点的索引值即为要展现的幻灯片的索引值
		nowli = $(this).index();
		//有一个问题，当连续点击当前的幻灯片，也就是即将要展示的幻灯片和即将要离开的幻灯片索引值一样
		//就会出现bug,因此这种情况，函数不做处理，直接返回
		if(nowli==prevli)
		{
			return;
		}
		//当前点击小圆点添加active，其他的移除active
		$(this).addClass('active').siblings().removeClass('active');

		//根据nowli，和previl运行幻灯片
		move();
	});

	//点击向前切换换页的函数
	$prev.click(function () {
		//判断暴力操作的开关为trun，就跳出下面的函数操作，即禁止幻灯片变化
		if(ismove)
		{
			return;
		}
		//首次点击为false，可以通过上一步判断，上一步通过之后，将ismove设置为true
		//再次点击详情按钮的时候，此时ismove为true，无法进行幻灯片播放
		ismove = true;
		//向前翻页，即将要展示的幻灯片索引为点击小圆点过后保存的nowli减去1或者初始值0减去1，
		//注意，nowli从初始开始减，会导致索引为负数，需要在move函数做增加判断
		nowli--;
		//nowli变化之后，触发幻灯片移动函数
		move();
		//翻页之后，根据要展示幻灯片的索引改变对应小圆点的active
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	});

	//点击向后切换换页的函数
	$next.click(function () {
		//判断暴力操作的开关为trun，就跳出下面的函数操作，即禁止幻灯片变化
		if(ismove)
		{
			return;
		}
		//首次点击为false，可以通过上一步判断，上一步通过之后，将ismove设置为true
		//再次点击详情按钮的时候，此时ismove为true，无法进行幻灯片播放
		ismove = true;
		//向后翻页，即将要展示的幻灯片索引为点击小圆点过后保存的nowli加上1或者初始值0加上1
		//注意，nowli从索引最大值开始加，会导致索引超出索引范围，需要在move函数做增加判断
		nowli++;
		move();
		//翻页之后，根据要展示幻灯片的索引改变对应小圆点的active
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	});

	//定义定时器函数，三秒钟运动一次
	timer = setInterval(autoplay, 3000);

	//定义鼠标进入幻灯片区域的时候，清除幻灯片自动运动效果，也就是定时器
	$slide.mouseenter(function () {
		clearInterval(timer);
	});

	//鼠标离开，开启定时器
	$slide.mouseleave(function () {
		timer = setInterval(autoplay, 3000);
	});
	//定义自动幻灯片播放的函数
	function autoplay() {
		nowli++;
		move();
		$points.eq(nowli).addClass('active').siblings().removeClass('active');
	}

	function move() {
		//通过向前后向后按钮点击时，会造成索引为负数或者超出索引范围，需要判断
		//第一张幻灯片向前的时候
		if(nowli<0)
		{
			//第一个索引0减1为-1的时候，其实下一张图片就是索引中最后一个值的图片
			//此时将即将展示的幻灯片索引值设置最后一张图片的索引即可
			//而要离开图片的索引值为0
			nowli = $len - 1;
			prevli = 0;
			//先将即将展示的幻灯片放置于最左侧
			$li.eq(nowli).css({'left': -760});
			//然后当前幻灯片移动到幻灯片的初始位置
			// 并设置变化的动画效果
			$li.eq(nowli).animate({'left': 0},800,'easeOutExpo');
			// 将离开的幻灯去移动到最右侧
			// 设置回调函数，关闭防止暴力的开关
			$li.eq(prevli).animate({'left': 760},800,'easeOutExpo',function () {
				ismove = false;
			});
			//运动完成之后，当前幻灯片的索引值即为下次要离开的幻灯片的索引值
			prevli = nowli;
			//注意，特殊索引值的判断方法执行完成之后，立即返回，否则会继续往下，进行其他的判断方法
			return;
		}

		//最后一张幻灯片向后的时候
		if(nowli>$len - 1)
		{
			nowli = 0;
			prevli = $len - 1;
			//先将即将展示的幻灯片放置于最右侧
			$li.eq(nowli).css({'left': 760});
			//然后当前幻灯片移动到幻灯片的初始位置
			$li.eq(nowli).animate({'left': 0},800,'easeOutExpo');
			// 将离开的幻灯去移动到最左侧
			$li.eq(prevli).animate({'left': -760},800,'easeOutExpo',function () {
				ismove = false;
			});
			//运动完成之后，当前幻灯片的索引值即为下次要离开的幻灯片的索引值
			prevli = nowli;
			//注意，特殊索引值的判断方法执行完成之后，立即返回，否则会继续往下，进行其他的判断方法
			return;
		}
		// 判断nowli和prevli，如果当前点击的小圆点即即将要展示的幻灯片的索引，大于此前幻灯片的索引
		//那么此时的动画效果是，要展示的幻灯片从最右边出现，离去的幻灯片从左侧出去
		if(nowli>prevli)
		{
			//先将即将展示的幻灯片放置于最右侧
			$li.eq(nowli).css({'left': 760});
			//然后当前幻灯片移动到幻灯片的初始位置
			$li.eq(nowli).animate({'left': 0},800,'easeOutExpo');
			// 将离开的幻灯去移动到最左侧
			$li.eq(prevli).animate({'left': -760},800,'easeOutExpo', function () {
				ismove = false;
			});
			//运动完成之后，当前幻灯片的索引值即为下次要离开的幻灯片的索引值
			prevli = nowli;
		}
		//此时当前幻灯片的索引值小于即将要展示的幻灯片索引值
		else
		{
			//先将即将展示的幻灯片放置于最左侧
			$li.eq(nowli).css({'left': -760});
			//然后当前幻灯片移动到幻灯片的初始位置
			$li.eq(nowli).animate({'left': 0},800,'easeOutExpo');
			// 将离开的幻灯去移动到最右侧
			$li.eq(prevli).animate({'left': 760},800,'easeOutExpo', function () {
				ismove = false;
			});
			//运动完成之后，当前幻灯片的索引值即为下次要离开的幻灯片的索引值
			prevli = nowli;
		}

	}
});