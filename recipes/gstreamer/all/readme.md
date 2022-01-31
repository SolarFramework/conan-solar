#Gstreamer recipe

currently tested with 1.8.4 version
	
	conan create . 1.18.4@ -tf None -s arch=x86_64 -s compiler.cppstd=17 -s build_type=Debug --build=missing -o shared=True

- fix : 
	- some conflicts version with glib version on linux (harfbuzz), so need to set up glib in 2.69.3 in gstreamer.
	- TODO : harfbuzz mandatory? or disable. More generally, it will be necessary to work on the versions of dependencies to avoid issues.
