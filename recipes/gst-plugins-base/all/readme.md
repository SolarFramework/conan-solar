#Gst-plugin-base recipe

currently tested with 1.8.4 version
	
	conan create . 1.18.4@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True